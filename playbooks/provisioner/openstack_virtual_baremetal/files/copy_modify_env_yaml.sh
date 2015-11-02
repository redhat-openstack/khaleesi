#!/bin/bash

sed -i "s#http://10.0.0.1:5000/v2.0#$OS_AUTH_URL#g" {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/os_password: password/os_password: '"$OS_PASSWORD"'/g'  {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/CentOS-7-x86_64-GenericCloud-1503/{{ provisioner.image.name }}/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/node_count: 2/node_count: {{ provisioner.node_count }}/g'  {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/private_net: private/private_net: {{ tmp.node_prefix }}private/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/public_net: public/public_net: {{ tmp.node_prefix }}public/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/provision_net: provision/provision_net: {{ tmp.node_prefix }}provision/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/bmc_prefix: bmc/bmc_prefix: {{ tmp.node_prefix }}bmc/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/baremetal_prefix: baremetal/baremetal_prefix: {{ tmp.node_prefix }}baremetal/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/key_name: default/key_name: {{ tmp.node_prefix }}default/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/bmc_flavor: bmc/bmc_flavor: m1.small/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;
sed -i 's/external_net: external/external_net: nova/g' {{ instack_user_home }}/openstack-virtual-baremetal/{{ tmp.node_prefix }}env.yaml;

