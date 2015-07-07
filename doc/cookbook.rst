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

Create an ssh key pair::

    ssh-keygen

.. Note:: We assume that you will named the key : id_rsa and id_rsa.pub

Upload the public key to the root user of your baremetal virt host::

    ssh-copy-id -i id_rsa.pub root@mybox

Create a ksgen-settings file for Khaleesi to be able to get options and
settings::

    ksgen --config-dir=../khaleesi-settings/settings generate \
        --provisioner=manual \
        --product=rdo \
        --product-version=kilo \
        --product-version-build=last_known_good \
        --product-version-repo=delorean \
        --distro=centos-7.0 \
        --workarounds=enabled \
        --installer=rdo_manager \
        --installer-env=virthost \
        --installer-images=build \
        --installer-network=neutron \
        --installer-network-variant=gre \
        --installer-topology=minimal \
        --extra-vars product.repo_type_override=none \
        ksgen_settings.yml

If you want to have more informations about the options used by ksgen launch::

    ksgen --config-dir=../khaleesi-settings/settings generate

.. Note:: This output will give you all options available in ksgen tools, You
    can also check into :ref:`usage` for more examples.

Once all theses steps is done, you have a ksgen-settings file which contains all
settings for your deployment. Khaleesi will load all the variables from this
YAML file.

Review the ksgen_settings.yml file

Here we assume that $HOST correspond to your baremetal virt host::

    export HOST=mybox

Generate the host file::

    cat <<EOF > local_hosts
    localhost ansible_connection=local
    host0 ansible_ssh_host=$HOST ansible_ssh_user=stack ansible_ssh_private_key_file=~/.ssh/id_rsa
    undercloud ansible_ssh_host=undercloud ansible_ssh_user=stack ansible_ssh_private_key_file=~/.ssh/id_rsa

    [virthost]
    host0

    [local]
    localhost
    EOF

Test your ssh connection with the generated hosts file::

    ansible -m ping -i local_hosts all

The next step will run your intended deployment::

    kcli --settings ksgen_settings.yml --provision --install

or::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml
