#! /usr/bin/env bash
set -e -u

source settings.sh

ansible-playbook -i local_hosts  \
 playbooks/cleanup.yml \
    --extra-vars @settings.yml -v

