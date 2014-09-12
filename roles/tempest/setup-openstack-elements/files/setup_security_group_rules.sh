#!/bin/bash
source /root/keystonerc_demo
neutron security-group-rule-create --direction ingress --protocol icmp default
neutron security-group-rule-create --direction egress --protocol icmp default
neutron security-group-rule-create --direction ingress --protocol tcp default
neutron security-group-rule-create --direction egress --protocol tcp default

exit 0
