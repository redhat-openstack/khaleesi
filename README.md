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
    library = /path/to/khaleesi/library

The roles_path allows us to keep the root of khaleesi "clean", and put playbooks in a subdirectory without needing to use relative paths for the roles.

These can also be specified with environment variables, to make this easier to create scripts or run from jenkins.

    ANSIBLE_HOST_KEY_CHECKING=False
    ANSIBLE_ROLES_PATH=/path/to/khaleesi/roles
    ANSIBLE_LIBRARY=/path/to/khaleesi/library

To execute the foreman install with nodes from an existing OpenStack:

    ansible-playbook -i local_hosts foreman.yml

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
