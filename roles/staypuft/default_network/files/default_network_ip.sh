#!/bin/bash
virsh net-destroy default
virsh net-undefine default
virsh net-define /tmp/default-network.xml
virsh net-autostart default
virsh net-start default
