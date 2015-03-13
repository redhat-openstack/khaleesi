#!/bin/bash -ex
#script to be used with component_settings.sh

function ensure_khaleesi() {
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
    sudo yum install rsync python-pip python-virtualenv
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
    pip install -U ansible
    pip install markupsafe
}

function ensure_ksgen() {
    if ! which ksgen >/dev/null 2>&1; then
    pushd khaleesi/tools/ksgen
    python setup.py develop
    popd
    fi
    pushd khaleesi
    ksgen --config-dir ${CONFIG_BASE}/settings \
    generate \
    --rules-file ${CONFIG_BASE}/rules/unittest.yml \
    --provisioner-options=$PROVISION_OPTION \
    --tester-component $TEST_COMPONENT \
    --distro $DISTRO \
    --extra-vars "provisioner.key_file=${PRIVATE_KEY}" \
    --extra-vars "test.env_name=virt" \
    ksgen_settings.yml
    popd
}

function ensure_ansible_connection(){
    pushd khaleesi
    ansible -i component_unit_test_hosts  \
        -u cloud-user \
        --private-key=$PRIVATE_KEY \
        -vvvv -m ping all
    connection=$?
    popd
    echo $connection
}

function ensure_ssh_key() {
    if ! ensure_ansible_connection; then
        ssh-copy-id "${TESTBED_USER}@${TESTBED_IP}"
    else
        echo "ssh keys are properly set up"
    fi
}

function configure_ansible_hosts() {
    pushd khaleesi
    if  [ $PROVISION_OPTION == "skip_provision" ]; then
    cat <<EOF >component_unit_test_hosts
[testbed]
$TESTBED_IP groups=testbed ansible_ssh_host=$TESTBED_IP ansible_ssh_user=$TESTBED_USER

[local]
localhost ansible_connection=local
EOF
     else
cat <<EOF >component_unit_test_hosts
[local]
localhost ansible_connection=local
EOF
    fi
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
ssh_args = -o ControlMaster=auto -o ControlPersist=180s
pipelining=True
callback_plugins = plugins/callbacks/
EOF
    fi
    popd
}

function run_ansible() {
    pushd khaleesi
    ansible-playbook -vv \
    -u $TESTBED_USER \
    --private-key=${PRIVATE_KEY} \
    -i component_unit_test_hosts \
    --extra-vars @ksgen_settings.yml \
    playbooks/unit_test.yml
    popd
}

if [ ! -f component_settings.sh ]; then
     echo "settings not found"
     exit 1
fi

TOP=$(pwd)
source component_settings.sh
ensure_rpm_prereqs
ensure_component
ensure_khaleesi
ensure_component
ensure_ansible
ensure_ksgen
configure_ansible_hosts
configure_ansible_cfg
ensure_ssh_key
run_ansible
