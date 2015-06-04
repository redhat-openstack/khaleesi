Using Khaleesi
==============

Khaleesi is an ansible based deployment tool Red Hat Openstack CI is using for
automation. In order to work, khaleesi need a configuration file which is
provide by khaleesi-settings project. Khaleesi-settings provide the config
file using ksgen tool, located into khaleesi project.

    http://git.app.eng.bos.redhat.com/git/khaleesi-settings.git

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
    sudo yum -y install python-devel sshpass

Install the OpenStack clients::

    sudo yum install python-novaclient python-neutronclient python-glanceclient -y

.. _installation:

Installation
------------

Create or enter a folder where you want to check out the repos. We assume that
both repo and your virtual environment is in the same directory. Clone the
repos::

    git clone https://github.com/redhat-openstack/khaleesi.git
    git clone https://github.com/redhat-openstack/khaleesi-settings.git

read-only mirror::

    git clone http://git.app.eng.bos.redhat.com/git/khaleesi-settings.git

Gerrit::

    https://review.gerrithub.io/#/q/project:redhat-openstack/khaleesi

Create the virtual envionment, install ansible, ksgen and kcli utils::

    virtualenv venv
    source venv/bin/activate
    cd khaleesi
    cd tools/ksgen
    python setup.py develop
    cd ../kcli
    python setup.py develop
    cd ../..

Create the appropriate ansible.cfg for khaleesi::

    cp ansible.cfg.example ansible.cfg

If you don't have a key you need to create it and upload it to your remote host
or your tenant in blue if your using the Openstack provisoner.

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
For all of those, the settings are provide by khaleesi-settings through ksgen
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

The whole idea of the configuration repo is to break everything into small units
Lets use the installer folder as an example to describe how the configuration
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
(according to the additional flags) and list all yml file it finds under those
folders.

Then ksgen starts merging all YAML files using the parent folders as base,
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

.. _beaker:

Installing rdo-manager with Beaker provisioner
----------------------------------------------

Here, we will deploy an RHEL OSP director using Beaker environment.

First we create the appropriate configuration file with ksgen. Make sure that
you are in your virtual envirnment that you previously created. ::

    source venv/bin/activate

Generate the configuration with the following command::

    ksgen --config-dir=../khaleesi-settings/settings generate \
        --provisioner=beaker \
        --provisioner-site=bkr \
        --provisioner-distro=rhel \
        --provisioner-distro-version=7.1 \
        --provisioner-site-user=rdoci-jenkins \
        --product=rhos \
        --product-version=7_director \
        --product-version-build=latest \
        --product-version-repo=poodle \
        --distro=rhel-7.1 \
        --installer=rdo_manager \
        --installer-env=virthost \
        --installer-images=build \
        --installer-topology=minimal \
        ksgen_settings.yml

.. Note:: These run settings can get outdated. If you want to replicate a
   Jenkins job, the best solution is to check its configuration and use the
   commands found inside the "Build" section. You could find an example here_.

The result is a YAML file collated from all the small YAML snippets from
``khaleesi-settings/settings``. All the options are quite self-explanatory and
changing them is simple as well. The rule file is currently only used for
deciding the installer+product+topology configuration. Check out ksgen_ for
detailed documentation.

The next step will run your intended deployment::

    kcli --settings ksgen_settings.yml --provision --install --test

you can run kcli --help for details on the kcli tool

.. Note:: If you get various ansible related errors while running this command
   (for example ``ERROR: group_by is not a legal parameter in an Ansible task
   or handler``) then first check if you installed ansible in the virtual env,
   that you enabled the virtual env. If you have a system wide ansible
   installation, please also try removing it and try again.

If any part fails, you can ask for help on the internal #rdo-ci channel. Don't
forget to save the relevant error lines on something like pastebin_.

Using your new undercloud / overcloud
`````````````````````````````````````

When your run is complete (or even while it's running), you can log in to your
beaker machine::

    ssh root@<beaker>
    su stack

If you want to log to your new undercloud machine, just make on your beaker::

    ssh -F ssh.config.ansible undercloud

Here you could play with your newly created Overcloud

.. _centosci:

Installing rdo-manager with centosci provisioner
------------------------------------------------

Here the installation is quite similar with Beaker provisioner.
Just notice the changes into the configuration for ksgen::

    export CONFIG_BASE=<path>/khaleesi-settings

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
        --installer-env=virthost \
        --installer-images=build \
        --installer-network=neutron \
        --installer-network-variant=ml2-vxlan \
        --installer-topology=minimal \
        --extra-vars product.repo_type_override=none \
        ksgen_settings.yml

All the steps are similar with :ref:`beaker`

.. _manual:

Installing rdo-manager with manual provisioner
----------------------------------------------

Using the manual provisioner is quite similar than with ref:`beaker`

First we create the appropriate configuration file with ksgen. Make sure that
you are in your virtual envirnment that you previously created. ::

    source venv/bin/activate

Generate the configuration with the following command::

    ksgen --config-dir=../khaleesi-settings/settings generate \
        --provisioner=manual \
        --product=rhos \
        --product-version=7_director \
        --product-version-build=latest \
        --product-version-repo=poodle \
        --product-version-workaround=rhel-7.1 \
        --workarounds=enabled \
        --distro=rhel-7.1 \
        --installer=rdo_manager \
        --installer-env=virthost \
        --installer-images=build \
        --installer-topology=minimal \
        ksgen_settings.yml

You need to regenerate your inventory file or using another one ::

    cat <<EOF > local_hosts
    localhost ansible_connection=local
    host0 ansible_ssh_host=$HOST ansible_ssh_user=stack ansible_ssh_private_key_file=rhos-jenkins.pem
    undercloud ansible_ssh_host=undercloud ansible_ssh_user=stack ansible_ssh_private_key_file=rhos-jenkins.pem

    [virthost]
    host0

    [local]
    localhost

    EOF

The next step will run your intended deployment::

    kcli --settings ksgen_settings.yml --provision --install --test

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

Installing Openstack All-in-one in Blue using your own tenant
-------------------------------------------------------------

.. Note:: In the below example we assume that the tenant we got in 'Blue'
    environment is 'tenant1' and the user is 'user1'.
    Replace 'tenant1' with your tenant name and 'user1' with your user name in
    Blue. We also assume that the external IPs range we got here is
    '10.35.184.121-10.35.184.126' - Replace the public* entries below with your
    network data as supplied by the 'Blue' admin
    There are three networks - 'Default-mgmt' and 'Nested-bridge' which are
    already created and 'Private-network' which is a private network
    which we created before.
    For every network entry the name is the name of the network and the id is
    the id of the network 'Private-network' is a network we created before.
    We use cloud.key as the key file. We assume we have a file key file cloud.key.

Upload the key to Blue
``````````````````````

From you tenant go to: Compute -> Access & Security -> Key Pairs ->
Import Key Pair::

   Key Pair name: cloudkey
   Public Key: Copy the content of cloud.key.pub

In case your tenant and user are not in khaleesi add the following files:

.. Note:: Change the files below to reflect your environment Please change 'tenant1' and 'user1' with your tenant and user name

settings/provisioner/openstack/site/blue/tenant/tenant1.yml::

    --- !extends:common/image.yml
    provisioner:
        tenant_name: tenant1
        key_file: <absolute path to cloud.key file>
        key_name: cloudkey
        network:
            network_list:
                data:
                    name: Private-network
                    id: 4b8e57fc-394e-430e-ae57-3ab7df54e7a7
                external:
                    allocation_start: 10.35.184.121
                    allocation_end:  10.35.184.126

settings/provisioner/openstack/site/blue/user/user1.yml::

    --- !extends:../tenant/tenant1.yml
    provisioner:
        username: user1
        password: mypassword

From the khaleesi-settings directory run the following (Adjust as needed)::

    export TENANT=tenant1
    export USER=user1
    ksgen --config-dir=../khaleesi-settings/settings generate \
        --provisioner=openstack \
        --provisioner-site=blue \
        --provisioner-site-tenant=$TENANT \
        --provisioner-site-user=$USER \
        --product=rhos \
        --product-version=7.1 \
        --product-version-repo=puddle \
        --product-version-build=latest \
        --distro=rhel-7.1 \
        --installer=packstack \
        --installer-topology=all-in-one \
        --installer-network=neutron \
        --installer-network-variant=ml2-vxlan \
        --installer-messaging=rabbitmq \
        --extra-vars tmp.node_prefix="$TENANT-"\
        ksgen_settings.yml

.. Note:: tmp.node_prefix should be ended with '-' !! It's optional variable.

.. Note:: Tester: If you want to add a tester node you should add --tester=<tester type> to the ksgen command (e.g. --tester=tempest)

The above command should create the file ksgen_settings.yml in the current
directory. From Khaleesi directory run the following to provision the
instance and install OpenStack:

    kcli --settings ksgen_settings.yml --provision --install

Installing Openstack Multi Node in Blue using your own tenant
-------------------------------------------------------------

All the steps are the same as the All-in-one case. The only difference is
running the ksgen with the paramter --installer-topology=multi-node instead
of --installer-topology=all-in-one.
This will install 4 nodes: controller , network node and 2 compute nodes.

Installing Openstack on Bare Metal
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

