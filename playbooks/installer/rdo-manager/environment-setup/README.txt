This directory environment-setup is the correct location for tools that setup the undercloud and overcloud nodes by outside scripts or instack-virt-setup.  It is recommended if using khaleesi to provision the undercloud and overcloud nodes that the playbooks/provisioner directory is used to provision the nodes while any post provision steps move here.

Current supported environment setup types..
- baremetal
- virthost

http://docs.openstack.org/developer/tripleo-docs/environments/environments.html
