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

    http://docs.openstack.org/developer/tripleo-docs/environments/environments.html#minimum-system-requirements

.. Note:: There is an internal khaleesi-settings git repository that contains the settings and configuration for RHEL deployments.
     Do not attempt to use a RHEL bare metal host or RHEL options in ksgen using these instructions

Deploy rdo-manager
------------------

Installation:
`````````````

.. Note:: The following steps should be executed from the machine that will be operating Khaleesi, not the machine it will be installing the undercloud and overcloud on.

Get the code :

khaleesi on Github::

    git clone git@github.com:redhat-openstack/khaleesi.git

khaleesi-settings on Github::

    git clone git@github.com:redhat-openstack/khaleesi-settings.git

Install tools and system packages::

    sudo yum install -y python-virtualenv gcc

or on Fedora 22::

    sudo dnf install -y python-virtualenv gcc

Create the virtual environment, install ansible, and ksgen util::

    virtualenv venv
    source venv/bin/activate
    pip install ansible==1.9.2
    cd khaleesi/tools/ksgen
    python setup.py install
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
   environment variable. The base_dir value should point to the directory where khaleesi and khaleesi-settings have been cloned.

If you want to have more informations about the options used by ksgen launch::

    ksgen --config-dir=../khaleesi-settings/settings help

.. Note:: This output will give you all options available in ksgen tools, You
    can also check into :ref:`usage` for more examples.

Once all of these steps have been completed you will have a ksgen-settings file containing all the settings needed for deployment. Khaleesi will load all of the variables from this YAML file.

Review the ksgen_settings.yml file:

Deployment Execution:
`````````````````````

Run your intended deployment::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/full-job-no-test.yml

Cleanup
-------
After you finished your work, you can simply remove the created instances by::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i hosts playbooks/cleanup.yml


Building rpms
-------------
You can use khaleesi to build rpms for you.

If you want to test manually a rpm with a patch from gerrit you can use the khaleesi infrastructure to do that.

Setup Configuration:
````````````````````
What you will need:

Ansible 1.9 installed I would recommend on a virtualenv::

    virtualenv foobar
    source foobar/bin/activate
    pip install ansible==1.9.2


``rdopkg`` is what is going to do the heavy lifting

    https://github.com/redhat-openstack/rdopkg

There's a public repo for the up to date version that can be installed like this::

    wget https://copr.fedoraproject.org/coprs/jruzicka/rdopkg/repo/epel-7/jruzicka-rdopkg-epel-7.repo
    sudo cp jruzicka-rdopkg-epel-7.repo /etc/yum.repos.d

    yum install -y rdopkg

Newer fedora versions uses dnf instead of yum so for the last step use::

    dnf install -y rdopkg

You will aslo need a ``rhpkg`` or a ``fedpkg`` those can be obtained from yum or dnf::

    yum install -y rhpkg

or::

    yum install -y fedpkg

Again for newer fedora versions replace yum for dnf::

    dnf install -y rhpkg
    dnf install -y fedpkg


In khaleesi will build the package locally (on a /tmp/tmp.patch_rpm_* directory) but in
order to do that it needs a file called ``hosts_local`` on your khaleesi folder

The ``hosts_local`` should have this content::

    [local]
    localhost ansible_connection=local

ksgen_settings needed
`````````````````````

Once you've got that you need to setup what gerrit patch you want to test::


    export GERRIT_BRANCH=<the_branch>
    export GERRIT_REFSPEC=<the_refspec>
    export EXECUTOR_NUMBER=0; #needed for now


Then you'll need to load this structure into your ``ksgen_settings.yml``::

    patch:
      upstream:
        name: "upstream-<package>"
        url: "https://git.openstack.org/openstack/<package>"
      gerrit:
        name: "gerrit-<package>"
        url: "<gerrit_url>"
        branch: "{{ lookup('env', 'GERRIT_BRANCH') }}"
        refspec: "{{ lookup('env', 'GERRIT_REFSPEC') }}"
      dist_git:
        name: "openstack-<package>"
        url: "<dist-git_url>"
        use_director: False

There's two ways to do that:

Either set the values via extra-vars::

    ksgen --config-dir settings \
      generate \
        --distro=rhel-7.1 \
        --product=rhos \
        --product-version=7.0
        --extra-vars patch.upstream.name=upstream-<package> \
        --extra-vars patch.upstream.url=https://git.openstack.org/openstack/<package> \
        --extra-vars patch.gerrit.name=gerrit-<package> \
        --extra-vars patch.gerrit.url=<gerrit_url> \
        --extra-vars patch.gerrit.branch=$GERRIT_BRANCH \
        --extra-vars patch.gerrit.refspec=$GERRIT_REFSPEC \
        --extra-vars patch.dist_git.name=openstack-<package> \
        --extra-vars patch.dist_git.url=<dist-git_url> \
        --extra-vars @../khaleesi-settings/settings/product/rhos/private_settings/redhat_internal.yml \
        ksgen_settings.yml

Or if khaleesi already has the settings for package you are trying to build on khaleesi/settings/rpm/<package>.yml you can do this second method::

    ksgen --config-dir settings \
      generate \
        --distro=rhel-7.1 \
        --product=rhos \
        --product-version=7.0
        --rpm=<package>
        --extra-vars @../khaleesi-settings/settings/product/rhos/private_settings/redhat_internal.yml \
        ksgen_settings.yml

.. Note:: At this time this second method works only for instack-undercloud, ironic, tripleo-heat-templates and python-rdomanager-oscplugin


Playbook usage
``````````````

Then just call the playbook with that ksgen_settings::

    ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/build_gate_rpm.yml

When the playbook is done the generated rpms will be on the ``generated_rpms`` of your ``khaleesi`` directory


