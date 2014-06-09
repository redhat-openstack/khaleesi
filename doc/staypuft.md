Prereqs
-------

* The guest, instance or machine that ansible is making calls to must have the following rpms initially available.
    - libselinux-python.$arch.rpm
    - ntp.$arch.rpm
* Virtualenv

Installation
------------

    virtualenv ansible
    source ansible/bin/activate
    pip install ansible


    ANSIBLE_HOST_KEY_CHECKING=False
    ANSIBLE_ROLES_PATH=/path/to/khaleesi/roles
    ANSIBLE_LIBRARY=/path/to/khaleesi/library:$VIRTUAL_ENV/share/ansible
    ANSIBLE_LOOKUP_PLUGINS=/path/to/khaleesi/plugins/lookups

To execute the staypuft prep with a baremetal node (RHEL 6.5 or Fedora 19):

Inventory (staypuft_hosts):

    [staypuft]
    foreman ansible_ssh_host=ipaddress ansible_ssh_user=root

Command line:

    ansible-playbook -i staypuft_hosts playbooks/staypuft.yml \
        --extra-vars @repo_settings.yml \
        --extra-vars @settings.yml \
        --extra-vars yum_update=yes

After you have run this playbook, you can run the staypuft-installer on your
baremetal machine.

Once Staypuft is installed, you can run the VM population playbook

    ansible-playbook -i staypuft_hosts playbooks/staypuft/virt-populate.yml \
        --extra-vars @repo_settings.yml \
        --extra-vars @settings.yml \
