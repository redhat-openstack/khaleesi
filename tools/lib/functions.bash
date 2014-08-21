if [ -z ${FUNCTIONS_SOURCED+xxx} ]; then
FUNCTIONS_SOURCED=true

set -e -u
declare -a __init_exit_todo_list=()
declare -i __init_script_exit_code=0

declare -r SCRIPT_CMD="$0"
declare -r SCRIPT_PATH=$(readlink -f "$0")

declare -r RED='\e[31m'
declare -r GREEN='\e[32m'
declare -r YELLOW='\e[33m'
declare -r BLUE='\e[34m'
declare -r MAGENTA='\e[35m'
declare -r CYAN='\e[36m'
declare -r WHITE='\e[37m'
declare -r BOLD='\e[1m'
declare -r NORMAL='\e[0m'

log_info() {
    echo -e "$BLUE${BOLD}INFO:$NORMAL" "$@"
}

log_error() {
    echo -e "$RED${BOLD}ERROR:$NORMAL" "$@"
}

log_warning() {
    echo -e "${RED}WARNING:$NORMAL" "$@"
}

debug.print_callstack() {
    local i=0;
    local cs_frames=${#BASH_SOURCE[@]}

    echo "--------------------------------------------------"
    echo "Traceback ... "
    for (( i=$cs_frames - 1; i >= 2; i-- )); do
        local cs_file=${BASH_SOURCE[i]}
        local cs_fn=${FUNCNAME[i]}
        local cs_line=${BASH_LINENO[i-1]}

        # extract the line from the file
        local line=$(sed -n "${cs_line}{s/^ *//;p}" "$cs_file")

        echo -e "  $cs_file[$cs_line]:" \
            "$cs_fn:\t" \
            "$line"
    done
    echo "--------------------------------------------------"
}

# on_exit_handler <exit-value>
on_exit_handler() {
    # store the script exit code to be used later
    __init_script_exit_code=${1:-0}

    # print callstack
    test $__init_script_exit_code -eq 0 || debug.print_callstack

    echo "Exit cleanup ... ${__init_exit_todo_list[@]} "
    for cmd in "${__init_exit_todo_list[@]}" ; do
        echo "    running: $cmd"
        # run commands in a subshell so that the failures
        # can be ignored
        ($cmd) || {
            local cmd_type=$(type -t $cmd)
            local cmd_text="$cmd"
            local failed="FAILED"
            echo "    $cmd_type: $cmd_text - $failed to execute ..."
        }
    done
}

on_exit() {
    local cmd="$*"

    local n=${#__init_exit_todo_list[*]}
    if [[ $n -eq 0 ]]; then
        trap 'on_exit_handler $?' EXIT
        __init_exit_todo_list=("$cmd")
    else
        __init_exit_todo_list=("$cmd" "${__init_exit_todo_list[@]}") #execute in reverse order
    fi
}

init.print_result() {
    local exit_code=$__init_script_exit_code
    if [[  $exit_code == 0 ]]; then
        echo "$SCRIPT_CMD: PASSED"
    else
        echo "$SCRIPT_CMD: FAILED" \
             " -   exit code: [ $exit_code ]"
    fi
}

cat_file() {
    echo -e "$BOLD$BLUE----[ $1 ]---------------------------------------$NORMAL"
    execute cat $1 | sed -e "s/\(.*\)\(password\|pass\|passwd\)\(.*\)/\1\2 <rest of the line is hidden>/"
    echo -e "$BLUE---------------------------------------------------$NORMAL"
    return 0
}

execute() {
  echo "Execute Command:"
  echo "    $@"
  ${DRY_RUN:-false} || "$@"
}

fi # FUNCTIONS_SOURCED
