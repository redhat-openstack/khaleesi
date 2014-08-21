#! /usr/bin/env bash
set -e -u

declare -r SCRIPT_DIR=$(cd $(dirname "$0") && pwd)
cd $SCRIPT_DIR
source tools/lib/functions.bash


cleanup() {
  local settings_file=${1:-settings.yml}
  test -f $settings_file || {
   log_error  "No settings file: $settings_file"
   exit 1
  }

  log_info "** tear down all nodes **"
  log_info "** function output saved to teardown.txt **"
  local cmdline="ansible-playbook -i local_hosts
        playbooks/cleanup.yml --extra-vars @$settings_file -v "
  log_info "executing: $cmdline"
  execute $cmdline > teardown.txt 2>&1
}

cleanup "$@"
