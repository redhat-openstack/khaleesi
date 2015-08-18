Khaleesi - Cookbook
===================

By following these steps, you will be able to deploy rdo-manager using khaleesi
on a CentOS machine with a basic configuration

Requirements
------------

For deploying rdo-manager you will need at least a baremetal machine which must
has the following minimum system requirements::

    CentOS-7
    Virtualization hardware extenstions enabled (nested KVM is not supported)
    1 quad core CPU
    12 GB free memory
    120 GB disk space

Khaleesi driven RDO-Manager deployments only support the following operating systems::

    CentOS 7 x86_64 
    RHEL 7.1 x86_64 ( Red Hat internal deployments only ) 

See the following documentation for system requirements::

    https://repos.fedorapeople.org/repos/openstack-m/docs/master/environments/virtual.html#minimum-system-requirements

.. Note:: There is an internal khaleesi-settings git repository that contains the settings and configuration for RHEL deployments.
     Do not attempt to use a RHEL bare metal host or RHEL options in ksgen using these instructions

Deploy rdo-manager
------------------

Installation:
`````````````

Get the code :

khaleesi on Github::

    git clone git@github.com:redhat-openstack/khaleesi.git

khaleesi-settings on Github::

    git clone git@github.com:redhat-openstack/khaleesi-settings.git

Install tools and system packages::

    sudo yum install -y python-virtualenv gcc

or on Fedora 22::

    sudo dnf install -y python-virtualenv gcc

Create the virtual envionment, install ansible, ksgen and kcli utils::

    virtualenv venv
    source venv/bin/activate
    pip install ansible==1.9.1
    cd khaleesi/tools/ksgen
    python setup.py develop
    cd ../kcli
    python setup.py develop
    cd ../..

.. Note:: If you get a errors with kcli installation make sure you have all
    system development tools intalled on your local machine:
    python2-devel for Fedora CentOS

Configuration:
``````````````

Create the appropriate ansible.cfg for khaleesi::

    cp ansible.cfg.example ansible.cfg
    touch ssh.config.ansible
    echo "" >> ansible.cfg
    echo "[ssh_connection]" >> ansible.cfg
    echo "ssh_args = -F ssh.config.ansible" >> ansible.cfg

SSH Keys:
``````````````

.. Note:: We assume that you will named the key : ~/id_rsa and ~/id_rsa.pub

Ensure that your ~/.ssh/id_rsa.pub file is in /root/.ssh/authorized_keys file on the baremetal virt host::
    
    ssh-copy-id root@<ip address of baremetal virt host>


Deployment Configuration:
`````````````````````````

Export the ip or fqdn hostname of the test box you will use as the virtual host for osp-director::

    export TEST_MACHINE=<ip address of baremetal virt host>

Create a ksgen-settings file for Khaleesi to be able to get options and
settings::

    ksgen --config-dir=../khaleesi-settings/settings generate \
        --provisioner=manual \
        --product=rdo \
        --product-version=kilo \
        --product-version-build=last_known_good \
        --product-version-repo=delorean_mgt \
        --distro=centos-7.0 \
        --installer=rdo_manager \
        --installer-env=virthost \
        --installer-images=build \
        --installer-network=neutron \
        --installer-network-isolation=none \
        --installer-network-variant=gre \
        --installer-topology=minimal \
        --installer-tempest=disabled \
        --installer-deploy=plan \
        --workarounds=enabled \
        --extra-vars product.repo_type_override=none \
        --extra-vars @$CONFIG_BASE/hardware_environments/virt_default/hw_settings.yml \
        ksgen_settings.yml

.. Note:: The "base_dir" key is defined by either where you execute ksgen from or by the $WORKSPACE 
environment variable. The base_dir value should point to the directory where khaleesi and khaleesi-settings have been cloned.

If you want to have more informations about the options used by ksgen launch::

    ksgen --config-dir=../khaleesi-settings/settings help

.. Note:: This output will give you all options available in ksgen tools, You
    can also check into :ref:`usage` for more examples.

Once all theses steps is done, you have a ksgen-settings file which contains all
settings for your deployment. Khaleesi will load all the variables from this
YAML file.

Review the ksgen_settings.yml file

Deployment Execution:
`````````````````````

The next step will run your intended deployment::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml


KCLI:: 

    kcli --settings ksgen_settings.yml --provision --install

.. Note:: kcli is considered beta for rdo-manager

Jenkins:
--------

For using khaleesi with Jenkins, first of all see the steps :ref:`jenkins` part for setting
up a Jenkins slave and for use jjb.

If you want to setup a manual job on Jenkins you have to follow those steps:

Setup a slave (General):
````````````````````````

Check the option::

    Restrict where this project can be run

And put the name of your slave.

Clone the repositories (Source Code Management):
````````````````````````````````````````````````
Select the choice::

     Multiple SCMs

And put the urls of the khaleesi / khaleesi-settings repositories.
You need to specify to jenkins to checkout the repositories in a sub-directory::

    Check out to a sub-directory

And specify for each::

    khaleesi
    khaleesi-settings

Build Environment:
``````````````````
Check the option:

    Delete workspace before build starts

Build:
``````

Add a step::

    Virtualenv Builder

And select::

    Python version: System-CPython-2.7
    Nature: Shell

And put the above informations into the shell command::

    pip install -U ansible==1.9.2 > ansible_build; ansible --version
    source khaleesi-settings/jenkins/ansible_rdo_mang_settings.sh
    export CONFIG_BASE=$WORKSPACE/khaleesi-settings

    # install ksgen
    pushd khaleesi/tools/ksgen
    python setup.py develop
    popd

    pushd khaleesi
    # generate config
    ksgen --config-dir=$CONFIG_BASE/settings generate \
        --provisioner=centosci \
        --provisioner-site=default \
        --provisioner-distro=centos \
        --provisioner-distro-version=7 \
        --provisioner-site-user=rdo \
        --product=rdo \
        --product-version=kilo \
        --product-version-build=last_known_good \
        --product-version-repo=delorean_mgt \
        --distro=centos-7.0 \
        --installer=rdo_manager \
        --installer-deploy=templates \
        --installer-env=virthost \
        --installer-images=build \
        --installer-network=neutron \
        --installer-network-isolation=none \
        --installer-network-variant=ml2-vxlan \
        --installer-post_action=none \
        --installer-topology=minimal \
        --installer-tempest=disabled \
        --workarounds=enabled \
        --extra-vars product.repo_type_override=none \
        --extra-vars @$CONFIG_BASE/hardware_environments/virt_default/hw_settings.yml \
        ksgen_settings.yml

    # get nodes and run test
    set +e
    anscmd="stdbuf -oL -eL ansible-playbook -vv --extra-vars @ksgen_settings.yml"

    $anscmd -i local_hosts playbooks/full-job-no-test.yml
    result=$?

    infra_result=0
    $anscmd -i hosts playbooks/collect_logs.yml &> collect_logs.txt || infra_result=1
    $anscmd -i local_hosts playbooks/cleanup.yml &> cleanup.txt || infra_result=2

    if [[ "$infra_result" != "0" && "$result" = "0" ]]; then
        # if the job/test was ok, but collect_logs/cleanup failed,
        # print out why the job is going to be marked as failed
        result=$infra_result
        cat collect_logs.txt
        cat cleanup.txt
    fi

    exit $result

Post-build actions:
```````````````````

Add a post build action for collecting logs and required files for debuging and archived them::

    Archive the artifacts: **/collected_files/*.tar.gz, **/nosetests.xml, **/ksgen_settings.yml

If you run tempest during the deployment add the following step for collecting the tests result::

    Publish JUnit test result report
    Test Report XMLs : **/nosetests.xml
    Check : Test stability history

