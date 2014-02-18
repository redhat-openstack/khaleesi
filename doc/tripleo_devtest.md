TripleO Devtest setup using Khaleesi
====================================

Khaleesi can prepare lab machines (installed by Beaker) for running
TripleO Devtest.


Getting ready
-------------

    # run this on your local machine

    sudo yum install ansible
    git clone https://github.com/redhat-openstack/khaleesi
    cd khaleesi

    cat <<EOF > hosts
    [tripleo]
    my-machine.example.org  ansible_ssh_user=root
    EOF

    $EDITOR hosts  # provide fqdn of your lab machine


Install
-------

This will prepare the machine in your `hosts` for running
devtest.

    # run this on your local machine
    # make sure you're in the khaleesi directory
    # need --extra-vars="devtest_user=root" because of https://bugs.launchpad.net/tripleo/+bug/1278861

    ANSIBLE_ROLES_PATH=./roles ansible-playbook -i hosts --extra-vars="devtest_user=root" playbooks/tripleo/tripleo.yml


Running Devtest
---------------

Connect via ssh to the machine as `devtest` user, and check if
`~/.devtestrc` suits your needs. Then run this as `devtest` user,
ideally inside a `tmux` or `screen` session so that you can detach:

    # run this on the lab machine

    export TRIPLEO_ROOT=~/tripleo
    $TRIPLEO_ROOT/tripleo-incubator/scripts/devtest.sh --trash-my-machine

See
[devtest docs](http://docs.openstack.org/developer/tripleo-incubator/devtest.html)
for more detailed information about using Devtest.


What Khaleesi does
------------------

It ensures that on the target machine:

* qemu-kvm is present and kvm_intel is modprobed

* Libvirt is present and running

* Libvirt default storage pool is in `/home/vm_storage_pool` (to
  compensate for small size of root partition in Beaker installs)

* Squid is present and running on port 3128 as Devtest documentation
  suggests

* GNU Screen and Tmux are installed (running Devtest takes a long
  time, ability to detach from a session is useful)

* standard package group is installed (things like bash completion,
  wget, compression utilities, ...)

* devtest user is present and has passwordless sudo rights

* tripleo-incubator is cloned

* `~/.devtestrc` file with sane defaults is present
