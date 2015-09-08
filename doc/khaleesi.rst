Using Khaleesi
==============

Khaleesi is an ansible based deployment tool Red Hat Openstack CI is using for
automation. In order to work, khaleesi need a configuration file which is
provided by khaleesi-settings project. Khaleesi-settings provide the config
file using ksgen tool, located in khaleesi project.

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

Create or enter a folder where you want to check out the repos. We assume that
both repo and your virtual environment are in the same directory. Clone the
repos::

    git clone https://github.com/redhat-openstack/khaleesi.git
    or
    git clone https://github.com/redhat-openstack/khaleesi-settings.git

read-only mirror::

    git clone http://<redhat-internal-git-server>/git/khaleesi-settings.git

Gerrit::

    https://review.gerrithub.io/#/q/project:redhat-openstack/khaleesi

Create the virtual envionment, install ansible, ksgen and kcli utils::

    virtualenv venv
    source venv/bin/activate
    pip install ansible==1.9.1
    cd khaleesi
    cd tools/ksgen
    python setup.py develop
    cd ../kcli
    python setup.py develop
    cd ../..

Create the appropriate ansible.cfg for khaleesi::

    cp ansible.cfg.example ansible.cfg

If you don't have a key you need to create it and upload it to your remote host
or your tenant in blue if you are using the Openstack provisoner.

Copy your private key file that you will use to access instances to
``khaleesi/``. We're going to use the common ``example.key.pem`` key.::

    cp ../khaleesi-settings/settings/provisioner/openstack/site/qeos/tenant/keys/example.key.pem  <dir>/khaleesi/
    chmod 600 example.key.pem

.. _overview:

Overview
--------

By using Khaleesi you will need to choose which installer you want to use, on
which provisioner.The provisioners corresponding to the remote machines which
will host your environment.
Khaleesi provide two installers: rdo-manager and packstack,
and four provisioners: beaker, centosci, openstack and manual.
For all of those, the settings are provided by khaleesi-settings through ksgen
tool.
You will find configuration variable under the folder "settings":

settings::

    |-- provisioner
    |   |-- beaker
    |   |-- libvirt
    |   |-- openstack
    |   `-- rackspace
    |-- installer
    |   |-- foreman
    |   |-- opm
    |   |-- packstack
    |   |-- rdo_manager
    |   `-- staypuft
    |-- tester
    |   |-- integration
    |   |-- pep8
    |   |-- rally
    |   |-- rhosqe
    |   |-- tempest
    |   `-- unittest
    |-- product
    |   |-- rdo
    |   `-- rhos
    |-- distro

The whole idea of the configuration repo is to break everything into small units.
Let's use the installer folder as an example to describe how the configuration
tree is built.
When using ksgen with the following flags::

    --installer=packstack \
    --installer-topology=multi-node \
    --installer-network=neutron \
    --installer-network-variant=ml2-vxlan \
    --installer-messaging=rabbitmq \

When the given --installer=packstack, ksgen is going to the folder called
"installer" in khaleesi-settings and looking for a "packstack.yml" file.

after that, it goes down the tree to the folder
"packstack/topology/multi-node.yml" (because of the flag
--installer-topology=multi-node), "packstack/network/neutron.yml", etc
(according to the additional flags) and list all yml files it finds under those
folders.

Then ksgen starts merging all YAML files using the parent folders as a base,
that means, that packstack.yml (which holds configuration that is common to
packstack) will be used as base and be merged with
"packstack/topology/multi-node.yml" and "packstack/network/neutron.yml"
and so on.

.. _usage:

Usage
-----

After you have everything set up, let's see how you can create machines using
rdo-manager or packstack installer. In both cases we're going to use
ksgen_ (Khaleesi Settings Generator) for supplying Khaleesi's ansible
playbooks_ with a correct configuration.

.. _ksgen: https://github.com/redhat-openstack/khaleesi/tree/master/tools/ksgen
.. _playbooks: http://docs.ansible.com/playbooks_intro.html
.. _here: https://ci.centos.org/view/rdo/job/rdo_manager-gate_khaleesi-none-7-rdo-kilo-delorean_mgt-centos-7.0-virthost-minimal-neutron-ml2-vxlan/
.. _pastebin: http://fpaste.org/

.. _manual:

Installing rdo-manager with the manual provisioner
----------------------------------------------

Here, we will deploy a RDO-Manager environment using the manual environment.

First, we create the appropriate configuration file with ksgen. Make sure that
you are in your virtual environment that you previously created. ::

    source venv/bin/activate

Export the ip or fqdn hostname of the test box you will use as the virtual host for osp-director::

    export TEST_MACHINE=<ip address of baremetal virt host>

Generate the configuration with the following command::

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
        --installer-deploy=plan \
        --installer-tempest=disabled \
        --workarounds=enabled \
        --extra-vars product.repo_type_override=none \
        --extra-vars @../khaleesi-settings/hardware_environments/virt_default/hw_settings.yml \
        ksgen_settings.yml

.. Note:: The "base_dir" key is defined by either where you execute ksgen from or by the $WORKSPACE 
environment variable.  The base_dir value should point to the directory where khaleesi and khaleesi-settings have been cloned. 

The result is a YAML file collated from all the small YAML snippets from
``khaleesi-settings/settings``. All the options are quite self-explanatory and
changing them is simple as well. The rule file is currently only used for
deciding the installer+product+topology configuration. Check out ksgen_ for
detailed documentation.

The next step will run your intended deployment::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml


If any part fails, you can ask for help on freenode #rdo channel. Don't
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

Here the installation is quite similar with Beaker provisioner.
Just notice the changes into the configuration for ksgen::

    ksgen --config-dir=../khaleesi-settings/settings generate \
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
    --installer-env=virthost \
    --installer-images=build \
    --installer-network=neutron \
    --installer-network-isolation=none \
    --installer-network-variant=ml2-vxlan \
    --installer-topology=minimal \
    --installer-tempest=disabled \
    --installer-deploy=plan \
    --workarounds=enabled \
    --extra-vars product.repo_type_override=none \
    --extra-vars @../khaleesi-settings/hardware_environments/virt_default/hw_settings.yml \
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
----------------------------------

All the steps are the same as the All-in-one case. The only difference is
running the ksgen with differents paramters:
Please change the below settings to match your environment::

    ksgen --config-dir=/khaleesi_project/khaleesi-settings/settings generate \
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

    kcli --settings ksgen_settings.yml --provision --install

Cleanup
-------
After you finished your work, you can simply remove the created instances by::

    kcli cleanup
