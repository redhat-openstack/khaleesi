#! /usr/bin/env bash
set -e -u
source functions.bash

collect_logs() {
  echo "** collecting logs from all nodes **"
  echo "** function output saved to collect_logs.txt **"
  local cmdline="ansible-playbook -v -s -i local_hosts  \
             playbooks/collect_logs.yml \
             --extra-vars @settings.yml   \
             --extra-vars @nodes.yml"

  [[ -n ${SKIP_TAGS:-''} ]] && cmdline+=" --skip-tags ${SKIP_TAGS#--skip_tags}"
  execute $cmdline > collect_logs.txt 2>&1
}

snapshot() {
  local cmdline="ansible-playbook -v -i local_hosts  \
    playbooks/snapshot.yml \
      --extra-vars @settings.yml  \
        --extra-vars @nodes.yml  \
          --extra-vars @job_settings.yml  \
            --tags=snapshot"
  [[ -n ${REMOTE_USER:-''} ]] && cmdline+=" -u $REMOTE_USER -s"
  execute $cmdline
}

validate_openstack() {
  local cmdline="ansible-playbook -v -s -i local_hosts  \
             playbooks/validate_openstack.yml \
             --extra-vars @settings.yml   \
             --extra-vars @nodes.yml "

  [[ -n ${SKIP_TAGS:-''} ]] && cmdline+=" --skip-tags ${SKIP_TAGS#--skip_tags}"
  execute $cmdline
}


main() {
    local default_playbook='aio.yml'

    if [ ! -e nodes.yml ]; then
        echo "Please create a nodes.yml file to define your environment"
        echo "See https://github.com/redhat-openstack/khaleesi/blob/master/doc/packstack.md"
        return 1
    fi


    parse_settings_args "$@"
    local playbook=${PLAYBOOK:-$default_playbook}

    # If the playbook does NOT contain a '/', default to the packstack playbooks
    [[ $playbook =~ '/' ]] ||  playbook="playbooks/packstack/$playbook"
    echo -e "\nPlaybook: $playbook"

    if $USE_PYTHON_GENERATOR; then
        execute python settings.py $SETTINGS_ARGS \
            -o settings.yml
    else
        generate_settings_file
    fi

    ### todo: add  --no-color option
    export ANSIBLE_FORCE_COLOR=true
    local cmdline="ansible-playbook -v -s -i local_hosts $playbook \
                   --extra-vars @settings.yml "

    echo -n "Settings files: settings.yml"
    if [[ -e repo_settings.yml ]]; then
        echo -n ", repo_settings.yml"
        cmdline+=" --extra-vars @repo_settings.yml"
    fi

    if  [[ -e job_settings.yml ]]; then
        echo -n ", job_settings.yml"
        cmdline+=" --extra-vars @job_settings.yml"
    fi
    echo
    cmdline+=" --extra-vars @nodes.yml"

    ## print the settings.yml but HIDE the password
    cat_file settings.yml |
        sed -e "s/\(.*\)\(password\|pass\|passwd\)\(.*\)/\1\2 <rest of the line is hidden>/"

    test -e repo_settings.yml && cat_file repo_settings.yml
    test -e job_settings.yml  && cat_file job_settings.yml

    # tags and skip tags
    # Remove extraneous '--tags' first.
    #Jobs that use this should switch to just providing the tags
    [[ -n ${TAGS:-''} ]] && cmdline+=" --tags ${TAGS#--tags=}"
    [[ -n ${SKIP_TAGS:-''} ]] && cmdline+=" --skip-tags ${SKIP_TAGS#--skip_tags}"

    local khaleesi_verbose=${KHALEESI_VERBOSE:-false}
    local khaleesi_ssh_verbose=${KHALEESI_SSH_VERBOSE:-false}
    if $khaleesi_verbose || $khaleesi_ssh_verbose; then
        cmdline+=" -v"
        $khaleesi_ssh_verbose && cmdline+="vvv"
    fi

    if ${VALIDATE_OPENSTACK:-false};then
        on_exit validate_openstack
    fi

    # collect logs only if the settings are proper
    on_exit collect_logs
    if ${TAKE_SNAPSHOT:-false}; then
        on_exit snapshot
    fi
    execute $cmdline
}

# requires a 0 exit code for clean.sh to execute
on_exit init.print_result
main "$@" || true
