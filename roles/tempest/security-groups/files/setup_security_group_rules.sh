#!/bin/bash
source /root/keystonerc_admin

# First remove all rules from the default group
for rule in `neutron security-group-rule-list | grep default | awk '{print $2}'`; do neutron security-group-rule-delete $rule; done

# Populate the default sec-group to allow communication
neutron security-group-rule-create --direction ingress default
neutron security-group-rule-create --direction egress default

exit 0
