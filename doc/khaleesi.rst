Using Khaleesi
==============

Khaleesi is an ansible based deployment tool for OpenStack. It was developed
by the Red Hat Openstack CI team and is used to simplify automation and builds.
In order to work, khaleesi needs a configuration file which can either be
provided by khaleesi-settings project. Khaleesi-settings populates the config
file using the ksgen (Khaleesi settings generator) tool, located in khaleesi project.

    https://github.com/redhat-openstack/khaleesi-settings
    or
    http://<redhat-internal-git-server>/git/khaleesi-settings.git

.. _prereqs:

Prerequisites
-------------

Fedora21+ with Python 2.7. For running jobs,
khaleesi requires a dedicated RHEL7 or F21 Jenkins slave. We do have an ansible
playbook that sets up a slave, see :ref:`jenkins-slave`.

.. WARNING:: Do not use the root user, as these instructions assumes that you
   are a normal user and uses venv. Being root may shadow some of the errors
   you may make like forgetting to source venv and pip install ansible.

Update your system, install git and reboot::

    sudo yum -y update && sudo yum -y install git && sudo reboot

Install the 'Development Tools' Package group, python-devel and
sshpass packages::

    sudo yum group install -y 'Development Tools'
    sudo yum -y install python-devel python-virtualenv sshpass

Install the OpenStack clients::

    sudo yum install python-novaclient python-neutronclient python-glanceclient -y

.. _installation:

Installation
------------

Create or enter the directory where you want to check out the repositories. We assume that
both the repositories and your virtual environment are in the same directory. Clone the
repositories::

    git clone https://github.com/redhat-openstack/khaleesi.git
    or
    git clone https://github.com/redhat-openstack/khaleesi-settings.git

read-only mirror::

    git clone http://<redhat-internal-git-server>/git/khaleesi-settings.git

Gerrit::

    https://review.gerrithub.io/#/q/project:redhat-openstack/khaleesi

Create the virtual environment, install ansible, ksgen and kcli utils::

    virtualenv venv
    source venv/bin/activate
    pip install ansible==1.9.2
    cd khaleesi
    cd tools/ksgen
    python setup.py develop
    cd ../kcli
    python setup.py develop
    cd ../..

Create the appropriate ansible.cfg for khaleesi::

    cp ansible.cfg.example ansible.cfg

If you are using the OpenStack provisioner, ensure that you have a key
uploaded on your remote host or tenant.

Copy the private key file that you will use to access instances to
``khaleesi/``. We're going to use the common ``example.key.pem`` key.::

    cp ../khaleesi-settings/settings/provisioner/openstack/site/qeos/tenant/keys/example.key.pem  <dir>/khaleesi/
    chmod 600 example.key.pem

.. _overview:

Overview
--------

To use Khaleesi you will need to choose an installer as well as
onto which type of provisioner you wish to deploy.The provisioners correspond to the
remote machines which will host your environment. Khaleesi currently provide five
installers and ten provisioners. For all combinations, the settings are provided
by khaleesi-settings through ksgen tool.
You will find configuration variables under in the *settings* directory:

settings::

    |-- provisioner
    |   |-- beaker
    |   |-- centosci
    |   |-- ec2
    |   |-- foreman
    |   |-- libvirt
    |   |-- manual
    |   |-- openstack
    |   |-- openstack_virtual_baremetal
    |   |-- rackspace
    |   | -- vagrant
    |-- installer
    |   |-- devstack
    |   |-- opm
    |   |-- packstack
    |   |-- project
    |   |-- rdo_manager
    |-- tester
    |   |-- api
    |   |-- component
    |   |-- functional
    |   |-- integration
    |   |-- pep8
    |   |-- rally
    |   |-- rhosqe
    |   |-- tempest
    |   |-- unittest
    |-- product
    |   |-- rdo
    |   |-- rhos
    |-- distro

One of Khaleesi's primary goals is to break everything into small units.
Let's use the installer directory as an example to describe how the configuration
tree is built.

Using ksgen with the following flags::

    --installer=packstack \
    --installer-topology=multi-node \
    --installer-network=neutron \
    --installer-network-variant=ml2-vxlan \
    --installer-messaging=rabbitmq \

When ksgen reads **--installer=packstack**, it will locate the *packstack.yml* file located within the *settings/installer* directory.

next it goes down the tree to the directory
*settings/packstack/topology/multi-node.yml* (because of the flag
--installer-topology=multi-node), *settings/packstack/network/neutron.yml*, etc
(according to the additional flags) and list all yml files it finds within those directories.

Then ksgen starts merging all YAML files using the parent directories as a base.
This means that *packstack.yml* (which holds configuration that is common to
packstack) will be used as base and be merged with
*settings/packstack/topology/multi-node.yml*, *settings/packstack/network/neutron.yml*,
and so on.

.. _usage:

Usage
-----

Once everything is set up we can see machines are created using either the
rdo-manager or packstack installer. In both cases we're going to use
ksgen to supply Khaleesi's ansible
playbooks_ with a correct configuration file.

.. _ksgen: https://github.com/redhat-openstack/khaleesi/tree/master/tools/ksgen
.. _playbooks: http://docs.ansible.com/playbooks_intro.html
.. _here: https://ci.centos.org/view/rdo/job/rdo_manager-gate_khaleesi-none-7-rdo-kilo-delorean_mgt-centos-7.0-virthost-minimal-neutron-ml2-vxlan/
.. _pastebin: http://fpaste.org/

.. _manual:

Installing rdo-manager with the manual provisioner
--------------------------------------------------

Here, we will deploy using the RDO-Manager provisioner and manual installer.

First, we create the appropriate configuration file with ksgen. Make sure that
you are in your virtual environment that you previously created. ::

    source venv/bin/activate

Export the ip or fqdn hostname of the test box you will use as the virtual host for osp-director::

    export TEST_MACHINE=<ip address of baremetal virt host>

Generate the configuration with the following command::

    ksgen --config-dir settings generate \
        --provisioner=manual \
        --product=rdo \
        --product-version=liberty \
        --product-version-build=last_known_good \
        --product-version-repo=delorean_mgt \
        --distro=centos-7.0 \
        --installer=rdo_manager \
        --installer-env=virthost \
        --installer-images=import_rdo \
        --installer-network-isolation=none \
        --installer-network-variant=ml2-vxlan \
        --installer-post_action=none \
        --installer-topology=minimal \
        --installer-tempest=smoke \
        --workarounds=enabled \
        --extra-vars @../khaleesi-settings/hardware_environments/virt/network_configs/none/hw_settings.yml \
        ksgen_settings.yml

.. Note:: The "base_dir" key is defined by either where you execute ksgen from or by the $WORKSPACE
   environment variable. The base_dir value should point to the directory where khaleesi and
   khaleesi-settings have been cloned.


The result is a YAML file collated from all the small YAML snippets from
``khaleesi-settings/settings`` (as described in ksgen_). All the options are quite self-explanatory and
changing them is simple. The rule file is currently only used for
deciding the installer+product+topology configuration. Check out ksgen_ for
detailed documentation.

The next step will run your intended deployment::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml


If any part fails, you can ask for help on the freenode #rdo channel. Don't
forget to save the relevant error lines on something like pastebin_.

Using your new undercloud / overcloud
`````````````````````````````````````

When your run is complete (or even while it's running), you can log in to your
test machine::

    ssh root@<test_machine>
    su stack

If you want to log to your new undercloud machine ::

    ssh -F ssh.config.ansible undercloud

Here you could play with your newly created Overcloud

.. _centosci:

Installing rdo-manager with centosci provisioner
------------------------------------------------

Here the installation is similiar to manual_ but we will use the centosci provisioner.
Notice the changes into the configuration for ksgen::

    ksgen --config-dir settings generate \
        --provisioner=centosci \
        --provisioner-site=default \
        --provisioner-distro=centos \
        --provisioner-distro-version=7 \
        --provisioner-site-user=rdo \
        --product=rdo \
        --product-version=liberty \
        --product-version-build=last_known_good \
        --product-version-repo=delorean_mgt \
        --distro=centos-7.0 \
        --installer=rdo_manager \
        --installer-env=virthost \
        --installer-images=import_rdo \
        --installer-network-isolation=none \
        --installer-network-variant=ml2-vxlan \
        --installer-post_action=none \
        --installer-topology=minimal \
        --installer-tempest=smoke \
        --workarounds=enabled \
        --extra-vars @../khaleesi-settings/hardware_environments/virt/network_configs/none/hw_settings.yml \
    ksgen_settings.yml


If any part fails, you can ask for help on the internal #rdo-ci channel. Don't
forget to save the relevant error lines on something like pastebin_.

Using your new undercloud / overcloud
`````````````````````````````````````

When your run is complete (or even while it's running), you can log in to your
host ::

    ssh root@$HOST
    su stack

If you want to log to your new undercloud machine, just make on your host::

    ssh -F ssh.config.ansible undercloud

Here you could play with your newly created Overcloud

.. _openstack:



Installing Openstack on Bare Metal via Packstack
------------------------------------------------

All the steps are the same as the All-in-one case. The only difference is
running the ksgen with different parameters:
Please change the below settings to match your environment::

    ksgen --config-dir settings generate \
    --provisioner=foreman \
    --provisioner-topology="all-in-one" \
    --distro=rhel-7.1 \
    --product=rhos \
    --product-version=7.0 \
    --product-version-repo=puddle \
    --product-version-build=latest \
    --extra-vars=provisioner.nodes.controller.hostname=puma06.scl.lab.tlv.redhat.com \
    --extra-vars=provisioner.nodes.controller.network.interfaces.external.label=enp4s0f1 \
    --extra-vars=provisioner.nodes.controller.network.interfaces.external.config_params.device=enp4s0f1 \
    --extra-vars=provisioner.nodes.controller.network.interfaces.data.label="" \
    --extra-vars=provisioner.nodes.controller.network.interfaces.data.config_params.device="" \
    --extra-vars=provisioner.network.network_list.external.allocation_start=10.35.175.1 \
    --extra-vars=provisioner.network.network_list.external.allocation_end=10.35.175.100 \
    --extra-vars=provisioner.network.network_list.external.subnet_gateway=10.35.175.101 \
    --extra-vars=provisioner.network.network_list.external.subnet_cidr=10.35.175.0/24 \
    --extra-vars=provisioner.network.vlan.external.tag=190 \
    --extra-vars=provisioner.remote_password=mypassword \
    --extra-vars=provisioner.nodes.controller.rebuild=yes \
    --extra-vars=provisioner.key_file=/home/itbrown/.ssh/id_rsa \
    --installer=packstack \
    --installer-network=neutron \
    --installer-network-variant=ml2-vxlan \
    --installer-messaging=rabbitmq \
    ksgen_settings.yml

And then simply run::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml


Installing Openstack on Bare Metal via rdo-manager
--------------------------------------------------

To deploy OpenStack RDO with rdo-manager you will need:
- an Undercloud: an existing machine running CentOS 7 since we use rdo-manager,
OSP-director requires RHEL7 instead
- a set of computer featuring power management interface supported
by _Ironic: .. http://docs.openstack.org/developer/tripleo-docs/environments/baremetal.html#ironic-drivers
- the undercloud machine must be able to reach the power management interfaces IP
- a hardware_environments in khaleesi settings as described below.

Testing Openstack Components
----------------------------

OpenStack components have various set of tests that are referred to as testers.
Below is a list of all testers that are supported in khaleesi, for running
tests on OpenStack components.The list is sorted by complexity of setting
up the environment needed for running the tests:

- pep8
- Unit tests
- Functional
- Integration
- API (in component repo)
- Tempest

Testers are passed to the ksgen CLI as '--tester=' argument value:
pep8, unittest, functional, integration, api, tempest

Below are examples on how to use the different testers:

To run pep8 you would use the following ksgen invocation:

  ksgen --config-dir settings \
  generate \
    --provisioner=openstack \
    --provisioner-site=qeos \
    --product=rhos \
    --distro=rhel-7.2 \
    --installer=project \
    --installer-component=nova \ # OpenStack component on which tests will run
    --tester=pep8
  ksgen_settings.yml

To run unit tests you would use the following ksgen invocation:

  ksgen --config-dir settings \
  generate \
    --provisioner=openstack \
    --provisioner-site=qeos \
    --product=rhos \
    --distro=rhel-7.2 \
    --installer=project \
    --installer-component=cinder
    --tester=unittest
  ksgen_settings.yml

To run functional tests, you would use:

  ksgen --config-dir settings \
  generate \
    --provisioner=openstack \
    --provisioner-site=qeos \
    --distro=rhel-7.2 \
    --product=rhos \
    --installer=packstack \
    --installer-config=full \ # To install single component use basic_neutron
    --tester=functional \
    --installer-component=neutron
  ksgen_settings.yml

To run API in-tree tests, you would use:

  ksgen --config-dir settings \
  generate \
    --provisioner=openstack \
    --provisioner-site=qeos \
    --distro=rhel-7.2 \
    --product=rhos \
    --installer=packstack \
    --installer-config=basic_glance \
    --tester=api \
    --installer-component=glance
  ksgen_settings.yml

To run tempest tests, use this invocation:

  ksgen --config-dir settings \
  generate \
    --provisioner=openstack \
    --provisioner-site=qeos \
    --distro=rhel-7.2 \
    --product=rhos \
    --installer=packstack \
    --installer-config=basic_cinder \
    --tester=tempest \
    --tester-tests=cinder_full \ # For single component tests use cinder_full
    --tester-setup=git \ # To install with existing package, use 'rpm'
  ksgen_settings.yml

Key differences between testers:

- pep8 and unittest
  Do not require installed OpenStack environment while other testers does.

  That is why for the pep8 and unittest the installer is the actual project
  repo: '--installer=project'.

  For pep8 and unittest khaleesi run would look like this:
  provision -> install component git repo -> run tests.

  For any other tester khaleesi run would look like this:
  provision -> install OpenStack* -> copy tests to tester node -> run tests.

  * Using packstack or rdo-manager

- Tempest
  Holds all the tests in separate project.

  While any other testser can only run on single component, Tempest
  holds system wide tests that can test multiple component in single run.
  That's why you need to define the tests to run with
  '--tester-tests=neutron_full' in order to run single component tests.
  To run all tests simply use '--tester-tests=all'.

  Tempest itself, as tester framework, can be installed via source or rpm.
  You can control it with '--tester-setup=git' or '--tester-setup=rpm'.

For all testers khaleesi is collecting logs.
There are two type of logs:

    1. The actual tests run. Those are subunit streams that khaleesi converts
       to junitxml.
    2. Any additional files that are defined by user for archiving.

Note that pep8 doesn't generate subunit stream, so in this case, the tests
logs are simply capture of output redirection from running the tests and not
the subunit stream itself.


The hardware_environments
=========================

This directory will describe your platform configuration. It comes with the following
files:

- network_configs/bond_with_vlans/bond_with_vlans.yml: The network configuration, here
  `bond_with_vlans` is the name of our configuration, adjust the name for your configuration.
  You can also prepare a different network profile.
- hw_settings.yml: the configuration to pass to rdo-manager (floating_ip range, neutron
  internal vlan name, etc)
- vendor_specific_setup: this file is a shell script that will be use to pass extra configuration
  to your hardware environment (RAID or NIC extract configuration). The file must exist but can
  be just empty.
- instackenv.json: The list of the power management interfaces. The file is documented in rdo-manager
  documentation: .. https://repos.fedorapeople.org/repos/openstack-m/rdo-manager-docs/liberty/environments/baremetal.html#instackenv-json

You can find some configuration samples in the khaleesi-settings project: .. https://github.com/redhat-openstack/khaleesi-settings/tree/master/hardware_environments

Start your deployment
=====================

This is an example of a ksgen command line, adjust it to match your environment::

    ksgen --config-dir=settings generate
    --provisioner=manual \
    --installer=rdo_manager \
    --installer-deploy=templates \
    --installer-env=baremetal \
    --installer-images=import_rdo \
    --installer-network=neutron \
    --installer-network-isolation=bond_with_vlans \
    --installer-network-variant=ml2-vxlan \
    --installer-post_action=default \
    --installer-topology=minimal \
    --installer-tempest=minimal \
    --installer-updates=none \
    --distro=centos-7.0 \
    --product=rdo \
    --product-version-build=last_known_good \
    --product-version-repo=delorean_mgt \
    --product-version=liberty \
    --workarounds=enabled \
    --extra-vars @/khaleesi_project/khaleesi-settings/hardware_environments/my_test_lab/hw_settings.yml \
    /khaleesi_project/ksgen_settings.yml

Declare the `$TEST_MACHINE` environment. It should point on the IP of our Undercloud. You should also
be able to open a SSH connection as root::

    export TEST_MACHINE=<ip address of baremetal undercloud host>
    ssh root@$TEST_MACHINE
    # exit

You must create a new `local_host` file. Here again adjust the IP address of your Undercloud::

    cat <<EOF > local_hosts
    [undercloud]
    undercloud groups=undercloud ansible_ssh_host=<ip address of baremetal undercloud host> ansible_ssh_user=stack ansible_ssh_private_key_file=~/.ssh/id_rsa
    [local]
    localhost ansible_connection=local
    EOF

You can now call Khaleesi::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml

Cleanup
-------
After you finished your work, you can simply remove the created instances by::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i hosts playbooks/cleanup.yml
