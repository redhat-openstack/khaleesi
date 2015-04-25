#!/bin/bash

cd "{{ tempest.dir }}"
python {{ tempest.dir }}/tools/config_tempest.py \
  --out {{ tempest.dir }}/etc/tempest.conf \
  --debug  \
  --create \
  identity.uri http://{{ hostvars[nodes.controller.name].ansible_default_ipv4.address }}:5000/v2.0/ \
  compute.allow_tenant_isolation true \
  object-storage.operator_role SwiftOperator \
  identity.admin_password {{ hostvars[nodes.controller.name].admin_password|default('redhat') }} \
  identity.password {{ hostvars[nodes.controller.name].demo_password|default('secrete') }}

#identity.uri http://10.8.49.70:5000/v2.0/ \
#compute.allow_tenant_isolation true \
#object-storage.operator_role Member \
#identity.admin_password secret \
#identity.password secret \

#compute.image_ref fbcf3c0c-729f-47ec-b929-89c3716f2d78 \
#compute.image_ref_alt fbcf3c0c-729f-47ec-b929-89c3716f2d78 \
#compute.build_timeout 500 \
#compute.image_ssh_user cirros \
#compute.ssh_user cirros \
#network.build_timeout 500 \
#volume.build_timeout 500 \
#scenario.ssh_user cirros \
#scenario.img_dir $HOME/scenario_imgs
#
