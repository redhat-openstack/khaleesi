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

    http://docs.openstack.org/developer/tripleo-docs/environments/virtual.html

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
    pip install ansible==1.9.2
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
        --product-version=liberty \
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
        --extra-vars @../khaleesi-settings/hardware_environments/virt/network_configs/none/hw_settings.yml \
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

And then simply run::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml

Cleanup
-------
After you finished your work, you can simply remove the created instances by::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i hosts playbooks/cleanup.yml
