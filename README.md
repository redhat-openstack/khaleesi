Prereqs
-------

Virtualenv

Installation
------------

1. virtualenv ansible
2. ansible/bin/activate
3. pip install ansible

Now, copy group_vars/all.sample to group_vars/all. Set the variables for your environment. These can also be set on the command-line. See 
http://www.ansibleworks.com/docs/playbooks_variables.html#passing-variables-on-the-command-line

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

    ansible-playbook -i my_hosts playbooks/foreman/foreman-installer.yml

