#!/bin/bash
source ~/keystonerc_admin

# Get the admin tenant id
admin_tenant_id=$(keystone tenant-get admin | grep id | awk '{print $4}')
security_group_id=$(neutron security-group-list -c id -c tenant_id | grep $admin_tenant_id | awk '{print $2}')

# First remove all rules from the admin default group
for rule in `neutron security-group-rule-list -c id -c tenant_id | grep $admin_tenant_id | awk '{print $2}'`; do neutron security-group-rule-delete $rule; done

# Populate the default sec-group to allow communication
for direction in ingress egress; do neutron security-group-rule-create --direction $direction $security_group_id; done
