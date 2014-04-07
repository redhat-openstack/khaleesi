#! /usr/bin/env bash
set -e -u

source functions.bash

# Quick Instructions:
# export:
# IMAGE_ID to the id of the image
#
# Two networks are not required, but one is atm. "neutron net-list"
# export:
# NET_1
# NET_2
#
# KEY_FILE= full path to openstack private ssh key for instance
# SSH_KEY_NAME= name of ssh key in openstack
#
# TAGS='--tags=provision,prep'
# REMOTE_USER= [cloud-user,fedora]
#
generate_settings_file "$@"
