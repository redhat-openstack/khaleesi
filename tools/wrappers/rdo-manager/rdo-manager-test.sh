#!/bin/bash -ex
#script to be used with component_settings.sh

function ensure_khaleesi() {
    export GIT_SSL_NO_VERIFY=true;
    if [ ! -d khaleesi ]; then
    git clone $KHALEESI
    fi
    if [ ! -d khaleesi-settings ]; then
    git clone $KHALEESI_SETTINGS
    fi
    source khaleesi-settings/packstack/jenkins/ansible_settings.sh
    export CONFIG_BASE="${TOP}/khaleesi-settings"
}

function ensure_rpm_prereqs() {
    sudo yum install -y git rsync python-pip python-virtualenv gcc
}

function ensure_component() {
    if [ ! -d $TEST_COMPONENT ]; then
    git clone $TEST_COMPONENT_URL $TEST_COMPONENT
    fi
}

function ensure_ansible() {
    if [ ! -d ansible_venv ]; then
    virtualenv ansible_venv
    fi
    source ansible_venv/bin/activate
    pip install -U ansible==1.8.2
    pip install markupsafe
}

function ensure_ksgen() {
    if ! which ksgen >/dev/null 2>&1; then
    pushd khaleesi/tools/ksgen
    python setup.py develop
    popd
    fi
    pushd khaleesi
    export JOB_NAME=''
    export BEAKER_MACHINE=$TESTBED_IP
    ksgen --config-dir=$CONFIG_BASE/settings generate \
    --rules-file=$CONFIG_BASE/rules/instack-virt-rdo.yml \
    --provisioner=beaker \
    --provisioner-site=bkr \
    --provisioner-distro=$DISTRO \
    --provisioner-distro-version=$DISTRO_VERSION \
    --provisioner-site-user=rdoci-jenkins \
    --provisioner-options=skip_provision \
    --product-version=kilo \
    --product-version-build=last_known_good \
    --product-version-repo=delorean_mgt \
    --product-version-workaround=$DISTRO-$DISTRO_VERSION \
    --workarounds=disabled \
    --distro=$DISTRO-$DISTRO_VERSION \
    --installer-network=neutron \
    --installer-network-variant=gre \
    --installer-messaging=rabbitmq \
    --tester=tempest \
    --tester-setup=rpm \
    --tester-tests=minimal \
    --extra-vars product.repo_type_override=$YUM_REPO_OVERRIDE \
    ksgen_settings.yml
    popd
}

function ensure_ansible_connection(){
    pushd khaleesi
    cat <<EOF >instack_hosts
[instack-virt-host]
$TESTBED_IP groups=testbed ansible_ssh_host=$TESTBED_IP ansible_ssh_user=root

[local]
localhost ansible_connection=local
EOF

    ansible -i instack_hosts  \
        -u root \
        --private-key=$PRIVATE_KEY \
        -vvvv -m ping all
    connection=$?
    popd
    echo $connection
}

function ensure_ssh_key() {
    if ! ensure_ansible_connection; then
        ssh-copy-id "root@${TESTBED_IP}"
    else
        echo "ssh keys are properly set up"
    fi
}

function configure_ansible_hosts() {
    pushd khaleesi
    rm -Rf instack_hosts
    cat <<EOF >instack_hosts
[instack-virt-host]
$TESTBED_IP groups=testbed ansible_ssh_host=$TESTBED_IP ansible_ssh_user=stack

[local]
localhost ansible_connection=local
EOF
    popd
}

function configure_ansible_cfg() {
    pushd khaleesi
    if [ ! -f  ansible.cfg ]; then
    cat <<EOF >ansible.cfg
[defaults]
host_key_checking = False
roles_path = ./roles
library = ./library:$VIRTUAL_ENV/share/ansible/
ssh_args =  -F ssh.config.ansible
pipelining=True
callback_plugins = plugins/callbacks/
EOF
    fi
    popd
}

function run_ansible_cleanup() {
    pushd khaleesi
    ansible-playbook -vv \
    --private-key=${PRIVATE_KEY} \
    -i instack_hosts \
    --extra-vars @ksgen_settings.yml \
    playbooks/cleanup_libvirt.yml
    popd
}

function test_git_checkout() {
    if [ ! -d khaleesi-settings ]; then
     echo "khaleesi-settings not found"
     exit 1
    fi

    if [ ! -d khaleesi ]; then
         echo "khaleesi not found"
         exit 1
    fi
}

function run_ansible_rdo_manager() {
    pushd khaleesi
    ansible-playbook -vv \
    --private-key=${PRIVATE_KEY} \
    -i instack_hosts \
    --extra-vars @ksgen_settings.yml \
    playbooks/rdo-manager.yml
    popd
}

if [ ! -f rdo-manager-settings.sh ]; then
     echo "settings not found"
     exit 1
fi

TOP=$(pwd)
source rdo-manager-settings.sh
ensure_rpm_prereqs
ensure_component
ensure_khaleesi
test_git_checkout
ensure_component
ensure_ansible
ensure_ksgen
ensure_ansible_connection
configure_ansible_cfg
ensure_ssh_key
configure_ansible_hosts
run_ansible_cleanup
run_ansible_rdo_manager

