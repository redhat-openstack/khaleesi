#! /usr/bin/env bash
set -e -u

declare SCRIPT_DIR=$(cd $(dirname "$0") && pwd)
cd $SCRIPT_DIR/../   ### TODO: experimental

source $SCRIPT_DIR/functions.bash


usage() {
    local exit_val=${1:-1}

    read -r -d '' help <<EOF_HELP
Usage:
    $( basename $0)  --use <settings> <playbook>
    $( basename $0)  -h|--help

Options:
    --use <settings>            All settings needed by khaleesi should be passed to
                                in yaml format. Will fail without this argument
   -h|--help                    show this help
   --tags TAGS,...              execute only TAGS
   --skip-tags TAGS,...
   --no-logs                    do not collect logs after running playbook
   --take-snapshot              take snapshot of the VM after running playbook
   --only-create-run-settings   only run 'dump the settings' playbook
   --no-create-run-settings     skip dumping the settings
   --run-settings-file FILE     file to dump settings used when running the playbook
   --silent                     show only minimal details, skips showing files
   --dry-run                    Only print the commands that would be executed

Creating settings file:
   use khaleesi-settings utility to generate settings file

EOF_HELP
    # use stdout if exit value is 0 else stderr
    if [[ $exit_val -eq 0 ]]; then
       echo "$help"
    else
       echo "$help" >&2
    fi
    exit $exit_val
}

parse_args() {
    ### while there are args parse them
    while [[ -n "${1+xxx}" ]]; do
        case $1 in
        -h|--help)      SHOW_USAGE=true;   break ;;    # exit the loop
        -q|--silent)    SILENT=true; shift ;;
        --use)          SETTINGS_FILE=$2;  shift 2 ;;
        --no-logs)      COLLECT_LOGS=false; shift 1 ;;
        --take-snapshot)      TAKE_SNAPSHOT=true; shift ;;
        --run-settings-file)  RUN_SETTINGS_FILE=$2; shift 2 ;;
        --no-create-run-settings)    SKIP_RUN_SETTINGS_CREATION=true; shift ;;
        --only-create-run-settings)  ONLY_RUN_SETTINGS_CREATION=true; shift ;;
        --dry-run)  DRY_RUN=true; shift ;;
        *.yml)      PLAYBOOK=$1;  shift ;;
        *) ARGS_FOR_ANSIBLE+=" $1"; shift ;;   # pass anything that run.sh
                                               # doesn't need to ansible
        esac
    done
}


collect_logs() {
    ansible_playbook playbooks/collect_logs.yml $ARGS_FOR_ANSIBLE
}

take_snapshot() {
    ansible_playbook playbooks/snapshot.yml --tags=snapshot
}

ansible_playbook() {
    local playbook=$1; shift

    local cmdline="ansible-playbook -s -i local_hosts --extra-vars @${SETTINGS_FILE}"

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
        --extra-var "'run_settings_file=${RUN_SETTINGS_FILE}'"

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
}

main() {
    # set global defaults
    KHALEESI_VERBOSE=${KHALEESI_VERBOSE:-false}
    KHALEESI_SSH_VERBOSE=${KHALEESI_SSH_VERBOSE:-false}

    SHOW_USAGE=false
    COLLECT_LOGS=true
    TAKE_SNAPSHOT=false
    RUN_SETTINGS_FILE='run_settings.yml'
    SKIP_RUN_SETTINGS_CREATION=false
    ONLY_RUN_SETTINGS_CREATION=false
    ARGS_FOR_ANSIBLE=""
    SILENT=false
    DRY_RUN=false

    $SILENT || on_exit init.print_result
    parse_args "$@"
    validate_args

    $SILENT || cat_file $SETTINGS_FILE

    ## create build settings file unless skipped
    $SKIP_RUN_SETTINGS_CREATION || generate_build_settings
    $ONLY_RUN_SETTINGS_CREATION && exit 0

    # collect logs only if the settings are proper
    $COLLECT_LOGS  && on_exit collect_logs
    $TAKE_SNAPSHOT && on_exit take_snapshot

    echo -e "\nPlaybook: $PLAYBOOK"
    ansible_playbook $PLAYBOOK $ARGS_FOR_ANSIBLE
}

# requires a 0 exit code for clean.sh to execute
main "$@" || true
