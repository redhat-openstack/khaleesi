#! /usr/bin/env bash
set -e -u
source functions.bash
SETTINGS_FILE=${1:-run_settings.yml}

cleanup() {
  echo "** tear down all nodes **"
  echo "** function output saved to teardown.txt **"
  local cmdline="ansible-playbook -i local_hosts  \
                playbooks/cleanup.yml \
                --extra-vars @$SETTINGS_FILE -v "
  execute $cmdline > teardown.txt 2>&1
}

cleanup

