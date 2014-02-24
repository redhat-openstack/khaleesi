TripleO Tuskar setup using Khaleesi
===================================

Khaleesi can prepare lab machines (installed by Beaker) for
development of Tuskar API, Tuskarclient and Tuskar UI.


Devtest installation
--------------------

You need a deployed Devtest on a lab machine. (At least running Seed
and Undercloud are necessary for installing Tuskar.) See
[Devtest setup using Khaleesi](https://github.com/redhat-openstack/khaleesi/blob/master/doc/tripleo_devtest.md)
for information how to deploy Devtest easily.


Direct SSH access to Seed and Undercloud
----------------------------------------

Khaleesi needs to connect directly to your Seed and Undercloud
VMs. Usually they are not visible from outside the host machine
though, so SSH needs to be configured to proxy the access.

To connect directly to your VMs from your workstation, put a config
similar to this into your `~/.ssh/config`:

    Host tripleo-seed
      ProxyCommand ssh root@my-machine.example.org nc 192.0.2.1 22

    Host tripleo-undercloud
      ProxyCommand ssh root@my-machine.example.org nc 192.0.2.3 22

(Assuming that `my-machine.example.org` is your lab machine,
`192.0.2.1` is the seed address and `192.0.2.3` is the undercloud
address.)

Verify the config by trying to directly ssh into the Seed VM from your
workstation:

    ssh root@tripleo_seed

Note that you will be able to ssh into Undercloud only after Khaleesi
runs, because Khaleesi needs to alter `authorized_keys` on Undercloud.


Installation
------------

Make sure your `hosts` file in Khaleesi directory is set up alike:

    [tripleo]
    my-machine.example.org  ansible_ssh_user=root

    [tripleo_seed]
    tripleo_seed  ansible_ssh_user=root

    [tripleo_undercloud]
    tripleo_undercloud  ansible_ssh_user=heat-admin

(Note that Undercloud has `heat-admin` as management user, it doesn't
allow logging in as `root`.)

Then run this on your workstation:

    # make sure you're in the khaleesi directory
    # need --extra-vars="devtest_user=root" because of https://bugs.launchpad.net/tripleo/+bug/1278861

    ANSIBLE_ROLES_PATH=./roles ansible-playbook -i hosts --extra-vars="devtest_user=root" playbooks/tripleo/tuskar.yml


Running Tuskar services and commands
------------------------------------

Khaleesi sets up everything for running Tuskar development
environment, but doesn't run Tuskar API/UI, because the assumption is
that you will want to run them yourself, look at the logs and restart
as necessary.

    # ssh into the Undercloud from your machine
    ssh heat-admin@tripleo_undercloud

    # run these in undercloud tmux / screen / multiple terminals
    ./tuskar-api.sh     # run API
    ./tuskar-ui.sh      # run UI
    ./tuskar-shell.sh   # run bash where 'tuskar' command is available

`tuskar-dbsync` has already been run for you, but if you need to run
it again, you can run:

    ./tuskar-dbsync.sh  # runs DB migrations for Tuskar API

Accessing UI
------------

Port forwarding has been set up on the host machine by Khaleesi, just
point your browser to `http://my-machine.example.org:8111` to access
Undercloud Dashboard. (You must be running `./tuskar-api.sh` and
`tuskar-ui.sh` as described above.)

Editing Tuskar sources on workstation
-------------------------------------

Best approach is perhaps to use sshfs to mount remote `heat-admin`
home directory to a local directory of choice, like this:

    sshfs heat-admin@tripleo_undercloud:/home/heat-admin ~/undercloud
