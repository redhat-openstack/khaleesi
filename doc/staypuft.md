Prereqs
-------

* The guest, instance or machine that ansible is making calls to must have the following rpms initially available.
    - libselinux-python.$arch.rpm
    - ntp.$arch.rpm
* Virtualenv

Installation
------------

Install ansible
===============

    virtualenv ansible --system-site-packages
    source ansible/bin/activate
    pip install ansible
    pip install BeautifulsSoup4


    export ANSIBLE_HOST_KEY_CHECKING=False
    export ANSIBLE_ROLES_PATH=/path/to/khaleesi/roles
    export ANSIBLE_LIBRARY=/path/to/khaleesi/library:$VIRTUAL_ENV/share/ansible
    export ANSIBLE_LOOKUP_PLUGINS=/path/to/khaleesi/plugins/lookups


Install ksgen
=============

    pushd tools/ksgen/
    python setup.py develop
    popd


Create inventory file
--------------------

    inventory.ini

    [staypuft]
    staypuft_host ansible_ssh_host=<baremetal-ipaddress> ansible_ssh_user=root

Run
---

To execute the staypuft prep with a baremetal node (RHEL 6.5):

Generate a valid khaleesi configuration
=======================================

    pushd <khaleesi-settings-dir>
    ksgen --config-dir=settings generate \
        --rules-file=rules/staypuft-rhos-vagrant.yml \
            --distro=rhel-6.5 \
                ksgen_settings.yml
    popd

Launch a complete staypuft installation
=======================================

    pushd khaleesi
    ./run.sh -vvvv -i inventory.ini --silent --no-logs --use ksgen_settings.yml playbooks/staypuft.yml


This playbook will in turn call

- baremetal setup to prepare hosting of staypuft and deploy vm
- creation of staypuft vm through vagrant
- creation of 5 empty deploy vms
- deployement of a standard openstack installation (controller + compute + neutron + ceph node + spare box)

