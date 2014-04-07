#! /usr/bin/env bash
set -e -u
source functions.bash

execute ansible-playbook -i local_hosts  \
    playbooks/cleanup.yml \
    --extra-vars @settings.yml \
    --extra-vars @nodes.yml -v
