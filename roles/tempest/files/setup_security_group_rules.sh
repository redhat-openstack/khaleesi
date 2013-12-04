#!/bin/bash
source /root/keystonerc_demo
neutron security-group-rule-create --direction ingress --protocol icmp default
neutron security-group-rule-create --direction ingress --protocol tcp \
    --port_range_max 22 --port_range_min 22 default

exit 0
