Code Review (IMPORTANT)
-----------------------

Pull requests will not be looked at on khaleesi github. Code submissions should be done via gerrithub (https://review.gerrithub.io). Please sign up with https://www.gerrithub.io and your github credentials to make submissions. Additional permissions on the project will need to be done on a per-user basis.

Prereqs
-------

* The guest, instance or machine that ansible is making calls to must have the following rpms initially available.
    - libselinux-python.$arch.rpm
    - ntp.$arch.rpm
* Virtualenv

Installation
------------

1. virtualenv ansible
2. ansible/bin/activate
3. pip install ansible


Now, copy group_vars/all.sample to group_vars/all. Set the variables for your environment. These can also be set on the command-line. See 
http://www.ansibleworks.com/docs/playbooks_variables.html#passing-variables-on-the-command-line

Create a $HOME/.ansible.cfg with the following:

    [defaults]
    host_key_checking = False
    roles_path = /path/to/khaleesi/roles
    library = /path/to/khaleesi/library:$VIRTUAL_ENV/share/ansible
    lookup_plugins = /path/to/khaleesi/plugins/lookups

The roles_path allows us to keep the root of khaleesi "clean", and put playbooks in a subdirectory without needing to use relative paths for the roles.

These can also be specified with environment variables, to make this easier to create scripts or run from jenkins.

    ANSIBLE_HOST_KEY_CHECKING=False
    ANSIBLE_ROLES_PATH=/path/to/khaleesi/roles
    ANSIBLE_LIBRARY=/path/to/khaleesi/library:$VIRTUAL_ENV/share/ansible
    ANSIBLE_LOOKUP_PLUGINS=/path/to/khaleesi/plugins/lookups

To execute the foreman install with nodes from an existing OpenStack:

    ansible-playbook -i local_hosts foreman.yml

Getting nodes from an OpenStack
-------------------------------

In order to use the get_nodes roles, you will need to define a 'nodes' var in group_vars/all. See the sample file for guidance.

Running with existing nodes
---------------------------

If you'd like to use an existing set of nodes, you can put together an inventory file:

    [foreman_installer:children]
    foreman
    controller
    compute
    networker

    [foreman]
    myforemannode ansible_ssh_host=ipaddress ansible_ssh_private_key_file=keyfile \
    public_ip=floatingip private_ip=fixedip foreman_private_ip=192.168.200.2 \
    foreman_public_ip=192.168.201.2 priv_hostname=foreman.example.com

    [controller]
    ...

    [compute]
    ...

    [networker]
    ...


Fill out the other groups similarly. The extra variables should be set on all the hosts

Then run:

    ansible-playbook -i my_hosts playbooks/foreman/foreman.yml

Debugging
---------

To keep the files on the remote for perusal

    ANSIBLE_KEEP_REMOTE_FILES=1

To step through the playbook, add '--step' to the command line

Available plugins
-----------------

Lookup plugins
==============

Bugzilla lookup

    cp bugzilla.ini{.sample,}

Modify bugzilla.ini with your credentials and bugzilla url, and the statuses that you use for 'open' bugs. If the status matches on of these, 'yes' will be returned, otherwise will return 'no'.

Use in a when: phrase to signify whether something should run based on status of bug.

    when: "lookup('bz', '123456')|bool"

This will lookup up bug #123456, and check the status against open_statuses from bugzilla.ini and return 'yes' if matched. The '|bool' is necessary to translate it into a bool.