#! /usr/bin/env bash
set -e -u

source settings.sh

cmdline="ansible-playbook -i local_hosts  \
 playbooks/cleanup.yml \
    --extra-vars @settings.yml \
      --extra-vars @nodes.yml -v"

echo $cmdline
$cmdline

