#!/bin/bash -ex
#script to be used with component_settings.sh

function ensure_khaleesi() {
    if [ ! -d khaleesi ]; then
    git clone $KHALEESI
    fi
    if [ ! -d khaleesi-settings ]; then
    git clone $KHALEESI_SETTINGS
    fi
    export CONFIG_BASE="${TOP}/khaleesi-settings"
}

function ensure_rpm_prereqs() {
    sudo yum install -y rsync python-pip python-virtualenv gcc
}

function ensure_component() {
    if [ ! -d $TEST_COMPONENT ]; then
    git clone $TEST_COMPONENT_URL $TEST_COMPONENT
    pushd $TEST_COMPONENT
    git checkout $TEST_COMPONENT_BRANCH
    popd
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
    if [ $PROVISIONER != manual ]; then
    ksgen --config-dir ${CONFIG_BASE}/settings \
    generate \
    --provisioner=${PROVISIONER} \
    --provisioner-site=${SITE} \
    --provisioner-site-user=${TENANT} \
    --product=$PRODUCT_TYPE \
    --product-repo=$PRODUCT_REPO \
    --product-version=${PRODUCT_VERSION} \
    --distro=${DISTRO} \
    --installer=project \
    --installer-component=${TEST_COMPONENT} \
    --tester=${TESTER_TYPE} \
    ksgen_settings.yml

    else
    ksgen --config-dir ${CONFIG_BASE}/settings \
    generate \
    --provisioner=${PROVISIONER} \
    --product=$PRODUCT_TYPE \
    --product-repo=$PRODUCT_REPO \
    --product-version=${PRODUCT_VERSION} \
    --distro=${DISTRO} \
    --installer=project \
    --installer-component=${TEST_COMPONENT} \
    --tester=${TESTER_TYPE} \
    ksgen_settings.yml
    fi

    popd
}

function ensure_ansible_connection(){
    pushd khaleesi
    ansible -i local_hosts  \
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

function ensure_tenant_key() {
    if [ $PROVISIONER != "manual" ]; then
    KEY_FILE=`find . -iname "$TENANT.pem"`
    cp $KEY_FILE khaleesi
    chmod 600 khaleesi/$TENANT.pem
    fi
}

function configure_ansible_hosts() {
    if [ ! -f khaleesi/local_hosts ]; then
cat <<EOF >local_hosts
[local]	
localhost ansible_connection=local
EOF
    else
    	cp khaleesi/local_hosts .
    fi  
}


function configure_ansible_cfg() {
    cp khaleesi/ansible.cfg.example ansible.cfg
    sed -i "s/roles$/khaleesi\/roles/g" ansible.cfg  
    sed -i "s/library/khaleesi\/library/2" ansible.cfg
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

function run_ansible() {
    anscmd="stdbuf -oL -eL ansible-playbook -vvvv --extra-vars @khaleesi/ksgen_settings.yml"
    $anscmd -i khaleesi/local_hosts khaleesi/playbooks/full-job.yml
    
    infra_result=0
    $anscmd -i hosts khaleesi/playbooks/collect_logs.yml &> collect_logs.txt || infra_result=1
    $anscmd -i local_hosts khaleesi/playbooks/cleanup.yml &> cleanup.txt || infra_result=2
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
test_git_checkout
ensure_component
ensure_ansible
ensure_ksgen
configure_ansible_hosts
configure_ansible_cfg
ensure_tenant_key
ensure_ssh_key
run_ansible
