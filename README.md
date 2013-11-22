Prereqs:

Virtualenv

Installation:

1. virtualenv ansible
2. ansible/bin/activate
3. pip install -e 'git+https://github.com/ansible/ansible.git@devel#egg=Ansible'

The current code requires the devel version (1.4) of ansible, as there is a bug in
1.34 in with_together. Will update this when 1.4 is released (which I think is due
sometime in December 2013)

Now, copy group_vars/all.sample to group_vars/all. Set the variables for your environment


To execute the foreman install with nodes from an existing OpenStack:

ansible-playbook -i local_hosts foreman.yml

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

