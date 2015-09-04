#!/bin/bash -e
#script to be used with rdo-manager-settings.sh

function ensure_khaleesi() {
    printf '\n'; printf '*************'; printf " GET GIT REPOS "; printf '*************'; printf '\n\n'
    export GIT_SSL_NO_VERIFY=true;
    if [ ! -d khaleesi ]; then
    git clone $KHALEESI
    fi
    if [ ! -d khaleesi-settings ]; then
    git clone $KHALEESI_SETTINGS
    fi
    #source khaleesi-settings/packstack/jenkins/ansible_settings.sh
    export CONFIG_BASE="${TOP}/khaleesi-settings"
}

function ensure_rpm_prereqs() {
    printf '\n'; printf '**************'; printf " INSTALL REQUIRED RPMS "; printf '**************'; printf '\n\n'
    sudo yum install -y git rsync python-pip python-virtualenv gcc
}


function ensure_ansible() {
    printf '\n'; printf '**************'; printf " INSTALL ANSIBLE "; printf '**************'; printf '\n\n'
    if [ ! -d ansible_venv ]; then
    virtualenv ansible_venv
    fi
    source ansible_venv/bin/activate
    pip install -U ansible==1.9.2
    pip install markupsafe
}

function ensure_ksgen() {
    printf '\n'; printf '**************'; printf " CREATE KSGEN_SETTINGS.YML "; printf '**************'; printf '\n\n'
    if ! which ksgen >/dev/null 2>&1; then
    pushd khaleesi/tools/ksgen
    python setup.py develop
    popd
    fi
    pushd khaleesi
    export TEST_MACHINE=$TESTBED_IP
    ksgen --config-dir=../khaleesi-settings/settings generate \
    --provisioner=manual \
    --distro=$DISTRO-$DISTRO_VERSION \
    --product=$PRODUCT \
    --product-version=$PRODUCT_VERSION \
    --product-version-build=$PRODUCT_VERSION_BUILD \
    --product-version-repo=$PRODUCT_VERSION_REPO \
    --installer=rdo_manager \
    --installer-deploy=templates \
    --installer-env=virthost \
    --installer-images=$INSTALLER_IMAGES \
    --installer-network=neutron \
    --installer-network-isolation=$INSTALLER_NETWORK_ISOLATION \
    --installer-network-variant=$INSTALLER_NETWORK_VARIANT \
    --installer-post_action=$INSTALLER_POST_ACTION \
    --installer-topology=minimal \
    --installer-tempest=$INSTALLER_TEMPEST \
    --workarounds=enabled \
    --extra-vars product.repo_type_override=none \
    --extra-vars @../khaleesi-settings/hardware_environments/virt/network_configs/$INSTALLER_NETWORK_ISOLATION/hw_settings.yml \
    ksgen_settings.yml
    popd
}

function ensure_ansible_connection(){
    printf '\n'; printf '**************'; printf " TEST CONNECTION TO $TEST_MACHINE "; printf '**************'; printf '\n\n'
    ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@$TEST_MACHINE ls -la
    return $?
}

function ensure_ssh_key() {
    printf '\n'; printf '**************'; printf " ENSURE SSH KEYS ARE ON $TEST_MACHINE "; printf '**************'; printf '\n\n'
    ssh-copy-id -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "root@${TESTBED_IP}"
}


function configure_ansible_cfg() {
    printf '\n'; printf '**************'; printf " CREATE ANSIBLE.CFG "; printf '**************'; printf '\n\n'
    pushd khaleesi
    if [ ! -f  ansible.cfg ]; then
    cp ansible.cfg.example ansible.cfg
    echo "ssh_args = -F ssh.config.ansible" >> ansible.cfg
    touch ssh.config.ansible
    fi
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
    printf '\n'; printf '**************'; printf " CREATE ANSIBLE.CFG "; printf '**************'; printf '\n\n'
    pushd khaleesi
    ansible-playbook -vv \
    -i local_hosts \
    --extra-vars @ksgen_settings.yml \
    playbooks/full-job-no-test.yml
    popd
}

if [ ! -f rdo-manager-settings.sh ]; then
     echo "settings not found"
     exit 1
fi

TOP=$(pwd)
source rdo-manager-settings.sh
ensure_rpm_prereqs
ensure_khaleesi
test_git_checkout
ensure_ansible
ensure_ksgen
ensure_ssh_key
ensure_ansible_connection
configure_ansible_cfg
run_ansible_rdo_manager

