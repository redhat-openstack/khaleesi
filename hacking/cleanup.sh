#! /usr/bin/env bash
set -e -u
source functions.bash

cleanup() {
  echo "** tear down all nodes **"
  echo "** function output saved to teardown.txt **"
  local cmdline="ansible-playbook -i local_hosts  \
                playbooks/cleanup.yml \
                --extra-vars @run_settings.yml -v "
  execute $cmdline > teardown.txt 2>&1
}

cleanup

