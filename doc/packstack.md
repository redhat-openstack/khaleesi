Prereqs
---------

* The guest, instance or machine that ansible is making calls to must have the following rpms initially available.
    - libselinux-python.$arch.rpm
* Virtualenv

Installation
------------

    virtualenv ansible
    source ansible/bin/activate
    pip install ansible

Ansible configuration
-------------
Create a $HOME/.ansible.cfg with the following:

    [defaults]
    host_key_checking = False
    roles_path = /path/to/khaleesi/roles
    library = /path/to/khaleesi/library:$VIRTUAL_ENV/share/ansible
    lookup_plugins = /path/to/khaleesi/plugins/lookups

NOTE: If you set library in .ansible.cfg, and you try to update ansible, it will fail. You will need comment out the line with a '#', run 'pip uninstall ansible; pip install ansible' to fix.

Nodes:
  Create a nodes.yml file that defines the environment
    Example:
	nodes:
	  - name: "{{ node_prefix }}"
	    image_id: "{{ image_id }}"
	    key_name: "{{ ssh_key_name }}"
	    flavor_id: "{{ flavor_id }}"
	    network_ids: "{{ network_ids }}"
	    hostname: packstack.example.com
	    groups: "packstack,controller,compute,openstack_nodes,tempest,{{ config.product }},{{ config.netplugin }}"
	    packstack_node_hostgroup: packstack

RDO repository config:
  cp group_vars/repo_settings.yml.default repo_settings.yml
  NOTE: The repositories can be adjusted to suite your needs

Overrides and additional config:
  Additional config can be read in via a job_settings.yml  file

Execution:
Set the following variables:

export IMAGE_ID=55555
export NET_1=55555
export NET_2=55555
export KEY_FILE=$HOME/key_name.pem
export SSH_KEY_NAME=key_name
export TAGS='--tags provision,prep,run-packstack,tempest_setup,tempest_run'
export TEMPEST_TEST_NAME=[tempest,$tempest_test] e.g.  tempest.scenario.test_network_basic_ops

If workarounds are required
export TAGS='--tags provision,prep,workaround,run-packstack,tempest_setup,tempest_run'

./run.sh
./run.sh multinode.yml

To rerun tempest after a successful execution
export TAGS='--tags provision,tempest_run'
