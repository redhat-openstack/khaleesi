#! /usr/bin/env bash
set -e -u

declare -r SCRIPT_DIR=$(cd $(dirname "$0") && pwd)
cd $SCRIPT_DIR

source functions.bash

print_usage() {

    read -r -d '' help <<-EOF_HELP || true
Usage:
    $( basename $0)  --use <settings> <playbook>
    $( basename $0)  -h|--help

Options:
    --use <settings>            All settings needed by khaleesi should be passed to
                                in yaml format. Will fail without this argument
   -h|--help                    show this help
   --tags TAGS,...              execute only TAGS
   --skip-tags TAGS,...
   --inventory FILE             Specify an alternate inventory file than local_hosts
   --no-logs                    do not collect logs after running playbook
   --take-snapshot              take snapshot of the VM after running playbook
   --only-create-run-settings   only run 'dump the settings' playbook
   --create-run-settings        run 'dump the settings' playbook before running the
                                actual playbook
   --run-settings-file FILE     file to dump settings used when running the playbook
   --silent                     show only minimal details, skips showing files
   --verbose                    show a lot of output, enables -vvvv on ansible playbook
   --dry-run                    Only print the commands that would be executed

$BOLD${RED}Deprecated options: ${NORMAL}
   --no-create-run-settings     skip dumping the settings

Creating settings file:
   use khaleesi-settings utility to generate settings file

EOF_HELP

    echo -e "$help"
    return 0
}

usage() {
    local exit_val=${1:-1}

    if [[ $exit_val -eq 0 ]]; then
        print_usage
    else
        print_usage  >&2
    fi
    # use stdout if exit value is 0 else stderr
    exit $exit_val
}

parse_args() {
    ### while there are args parse them
    while [[ -n "${1+xxx}" ]]; do
        case $1 in
        -h|--help)      SHOW_USAGE=true;   break ;;    # exit the loop
        -q|--silent)    SILENT=true; shift ;;
        --verbose)      KHALEESI_VERBOSE=true; KHALEESI_SSH_VERBOSE=true; shift ;;
        --use)          SETTINGS_FILE=$2;  shift 2 ;;
        --no-logs)      COLLECT_LOGS=false; shift 1 ;;
        --take-snapshot)      TAKE_SNAPSHOT=true; shift ;;
        --create-run-settings)    CREATE_RUN_SETTINGS=true; shift ;;
        --only-create-run-settings)  ONLY_RUN_SETTINGS_CREATION=true
                                     CREATE_RUN_SETTINGS=true; shift ;;
        --run-settings-file)  RUN_SETTINGS_FILE=$2; shift 2 ;;
        --inventory) INVENTORY_FILE=$2; shift 2 ;;
        --no-create-run-settings) DEPRECATED_OPTIONS_USED=true; shift ;;
        --dry-run)  DRY_RUN=true; shift ;;
        *.yml)      PLAYBOOK=$1;  shift ;;
        *) ARGS_FOR_ANSIBLE+=" $1"; shift ;;   # pass anything that run.sh
                                               # doesn't need to ansible
        esac
    done
    return 0
}


collect_logs() {
    ansible_playbook playbooks/collect_logs.yml $ARGS_FOR_ANSIBLE > collect_logs.txt 2>&1
}

take_snapshot() {
    ansible_playbook playbooks/snapshot.yml --tags=snapshot
}

ansible_playbook() {
    local playbook=$1; shift
    local cmdline="ansible-playbook -i ${INVENTORY_FILE} --extra-vars @${SETTINGS_FILE}"

    if $KHALEESI_VERBOSE || $KHALEESI_SSH_VERBOSE; then
        cmdline+=" -v"
        $KHALEESI_SSH_VERBOSE && cmdline+="vvv"
    fi

    export ANSIBLE_FORCE_COLOR=true
    execute $cmdline $playbook "$@"
}


generate_build_settings() {
    echo "Generating build settings file"
    rm -f $RUN_SETTINGS_FILE
    ansible_playbook playbooks/dump_settings.yml \
         --extra-vars "'run_settings_file=${RUN_SETTINGS_FILE}'"

   $SILENT || cat_file $RUN_SETTINGS_FILE
}


validate_args() {
    # usage
    $SHOW_USAGE && usage 0      # if  --help show usage and exit 0

    # validation
    [ -z ${SETTINGS_FILE+xxx} ] && {
        log_error "No ${RED}settings${NORMAL} file passed: \
        did you forget ${BLUE}${BOLD}--use$NORMAL ?"
        usage   # exit 1 if no settings file
    }

    # no playbook and is not trying to generate
    # run_settings
    [ -z ${PLAYBOOK+xxx} ] && ! ${ONLY_RUN_SETTINGS_CREATION} &&  {
        log_error "No playbook file passed: \
        no $BLUE${BOLD}*.yml$NORMAL found in args "
        usage
     }

    $DEPRECATED_OPTIONS_USED && {
        log_warning "Deprecated options used: ${RED}Ignoring $NORMAL"
        echo -e $BOLD$RED------------------------------------------ $NORMAL
        print_usage
        echo -e '-----------------------------------------------------------\n'

    }
    return 0
}

main() {
    # set global defaults
    KHALEESI_VERBOSE=${KHALEESI_VERBOSE:-false}
    KHALEESI_SSH_VERBOSE=${KHALEESI_SSH_VERBOSE:-false}
    INVENTORY_FILE=${INVENTORY_FILE:-local_hosts}

    SHOW_USAGE=false
    COLLECT_LOGS=true
    TAKE_SNAPSHOT=false
    RUN_SETTINGS_FILE='run_settings.yml'
    ONLY_RUN_SETTINGS_CREATION=false
    ARGS_FOR_ANSIBLE=""
    SILENT=false
    DRY_RUN=false
    DEPRECATED_OPTIONS_USED=false
    CREATE_RUN_SETTINGS=false

    parse_args "$@"
    validate_args

    $SILENT || on_exit init.print_result
    $SILENT || cat_file $SETTINGS_FILE

    ## create build settings file unless skipped
    $CREATE_RUN_SETTINGS && generate_build_settings
    $ONLY_RUN_SETTINGS_CREATION && exit 0

    # collect logs only if the settings are proper
    $COLLECT_LOGS  && on_exit collect_logs
    $TAKE_SNAPSHOT && on_exit take_snapshot

    echo -e "\nPlaybook: $PLAYBOOK"
    ansible_playbook $PLAYBOOK $ARGS_FOR_ANSIBLE
}

main "$@"
