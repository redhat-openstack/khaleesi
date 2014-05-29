if [ -z ${FUNCTIONS_SOURCED+xxx} ]; then
FUNCTIONS_SOURCED=true

set -e -u
declare -a __init_exit_todo_list=()
declare -i __init_script_exit_code=0

declare -r SCRIPT_CMD="$0"
declare -r SCRIPT_PATH=$(readlink -f "$0")
declare -r TOP_DIR=$(cd $(dirname "$0") && pwd)

debug.print_callstack() {
    local i=0;
    local cs_frames=${#BASH_SOURCE[@]}

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
    echo "----- [ $1 ]---------------------------------------"
    cat $1
    echo "---------------------------------------------------"
}

execute() {
  echo "Execute Command:"
  echo "    $@"
  "$@"
}

parse_settings_args() {

    # default values for args
    USE_PYTHON_GENERATOR=false
    SETTINGS_ARGS=""

    ### while there are args parse them
    while [[ -n "${1+xxx}" ]]; do
        case $1 in
            --use-python-generator)
                USE_PYTHON_GENERATOR=true
                shift 1
                ;;
            --tags)
                TAGS=$2
                shift 2
                ;;
            --skip-tags)
                SKIP_TAGS=$2
                shift 2
                ;;
            -I|--inventory)
                INVENTORY_FILE=$2
                shift 2
                ;;
            -P|--playbook)
                PLAYBOOK=$2
                shift 2
                ;;
            -N|--nodes)
                NODES_FILE=$2
                shift 2
                ;;
            *.yml)
                PLAYBOOK=$1
                shift 1
                ;;
            --settings-path)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --build)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --tempest)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --site)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --installer)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --product)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --productreleaserepo)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --productrelease)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --distribution)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --distrorelease)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --topology)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --networking)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --variant)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --testsuite)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --job-name)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --set-variable)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --delete-variable)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --update-variable)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            --create-variable)
                SETTINGS_ARGS+=" $1 $2 "
                shift 2
                ;;
            *)
                printf >&2 'WARNING: unknown option: %s\n' $1
                shift
                ;;
        esac
    done
}

generate_settings_file() {
    local out_file=${1:-'settings.yml'}

    local OS_NETWORK_TYPE=${OS_NETWORK_TYPE:-'neutron'}
    local default_floating_nw_name='external'
    local default_flavor_id=4
    local default_tempest_flavor_id=2
    local default_tempest_image_id='10a4092c-6ec9-4ddf-b97c-b0f8dff0958e'
    local default_tempest_repo='git://github.com/openstack/tempest.git'

    local wait_for_boot=${WAIT_FOR_BOOT:-'180'}

    local key_file=${KEY_FILE:-/key.pem }
    local key_name=${SSH_KEY_NAME:-'key'}
    chmod 600 $key_file

    local job_name=${JOB_NAME}
    local node_prefix=${NODE_PREFIX:-''}
    local flavor_id=${FLAVOR_ID:-$default_flavor_id}
    local floating_nw_name=${FLOATING_NETWORK_NAME:-'external'}

    local image_id=$IMAGE_ID
    local tempest_image_id=${TEMPEST_IMAGE_ID:-$default_tempest_image_id}
    local tempest_flavor_id=${TEMPEST_FLAVOR_ID:-$default_tempest_flavor_id}
    local foreman_image_id=${FOREMAN_IMAGE_ID:-$IMAGE_ID}
    local foreman_flavor_id=${FOREMAN_FLAVOR_ID:-$default_flavor_id}
    local net_1=${NET_1:-'CHANGE_ME'}
    local net_2=${NET_2:-''}
    local net_2_name=${NET_2_NAME:-''}
    local net_3=${NET_3:-''}
    local net_3_name=${NET_3_NAME:-''}

    local tags=${TAGS:-''}
    local skip_tags=${SKIP_TAGS:-''}
    local skip_tags_collect=${SKIP_TAGS_COLLECT:-''}
    local tempest_tests=${TEMPEST_TEST_NAME:-'tempest.scenario.test_network_basic_ops'}
    local remote_user=${REMOTE_USER:-'cloud-user'}
    local tempest_repo=${TEMPEST_REPO:-$default_tempest_repo}
    local tempest_branch=${TEMPEST_BRANCH:-'master'}
    local tempest_remote_user=${TEMPEST_REMOTE_USER:-'fedora'}
    local tempest_setup_method=${TEMPEST_SETUP_METHOD:-'packstack/provision'}
    local foreman_remote_user=${FOREMAN_REMOTE_USER:-$REMOTE_USER}

    local sm_username=${SM_USERNAME:-''}
    local sm_password=${SM_PASSWORD:-''}

    local host_env=${HOST_ENV:-'neutron'}
    local product=${PRODUCT:-'rdo'} #product
    local productrelease=${PRODUCTRELEASE:-'icehouse'} #rdo_release
    local productreleaserepo=${PRODUCTRELEASEREPO:-'production'} #rdo_repo
    local netplugin=${NETPLUGIN:-'neutron'} #network_driver

    local update_rpms_tarball=${UPDATE_RPMS_TARBALL:-''}

    local net_ids="[{ net-id: '$net_1' }"
    if [[ ! -z $net_2 ]]; then
      net_ids="$net_ids, { net-id: '$net_2' }"
    fi
    if [[ ! -z $net_3 ]]; then
      net_ids="$net_ids, { net-id: '$net_3' }"
    fi
    net_ids="$net_ids ]"

cat > $out_file <<-EOF
# job config

packstack_int: whayutin

config:
  product: $product
  version: $productrelease
  repo: $productreleaserepo
  netplugin: $netplugin
  verbosity:
    - info

# OpenStack controller settings, can be set by sourcing a keystonerc file
os_auth_url: '$OS_AUTH_URL'
os_username: $OS_USERNAME
os_password: $OS_PASSWORD
os_tenant_name: $OS_TENANT_NAME
os_network_type: $OS_NETWORK_TYPE

# instance settings
job_name: $job_name
node_prefix: $node_prefix
network_ids: $net_ids
net_2_name: $net_2_name
net_3_name: $net_3_name
image_id: $image_id
ssh_private_key: $key_file
ssh_key_name: $key_name
flavor_id: $flavor_id
floating_network_name: $floating_nw_name
tempest_image_id: $tempest_image_id
tempest_flavor_id: $tempest_flavor_id
tempest_remote_user: $tempest_remote_user
foreman_image_id: $foreman_image_id
foreman_flavor_id: $foreman_flavor_id
foreman_remote_user: $foreman_remote_user
sm_username: $sm_username
sm_password: $sm_password

cleanup_nodes: "{{ nodes }}"

#VM settings
epel_repo: download.fedoraproject.org/pub/epel/6/
gpg_check: 0
ntp_server: clock.redhat.com
reboot_delay: +1
wait_for_boot: $wait_for_boot

update_rpms_tarball: $update_rpms_tarball

# Currently sudo w/ NOPASSWD must be enabled in /etc/sudoers for sudo to work
# running w/ -u $remote_user and -s will override these options
remote_user: $remote_user

tempest:
    setup_method: $tempest_setup_method
    repo: $tempest_repo
    revision: $tempest_branch
    checkout_dir: /var/lib/tempest
    puppet_file: /tmp/tempest_init.pp
    test_name: $tempest_tests
    exclude:
        files:
            - test_server_rescue
            - test_server_actions
            - test_load_balancer
            - test_vpnaas_extensions
        tests:
            - test_rescue_unrescue_instance
            - test_create_get_delete_object
            - test_create_volume_from_snapshot
            - test_service_provider_list
            - test_ec2_
            - test_stack_crud_no_resources
            - test_stack_list_responds

log_files:
  - /var/tmp/packstack
  - /root/
  - "{{ tempest.checkout_dir }}/etc/"
  - "{{ tempest.checkout_dir }}/run.log"
  - "{{ tempest.checkout_dir }}/tempest.log"
  - "{{ tempest.checkout_dir }}/*.log"
  - "{{ tempest.checkout_dir }}/*.xml"
  - /var/log/
  - /etc/nova
  - /etc/ceilometer
  - /etc/cinder
  - /etc/glance
  - /etc/keystone
  - /etc/neutron
  - /etc/ntp
  - /etc/puppet
  - /etc/qpid
  - /etc/qpidd.conf
  - /etc/selinux
  - /etc/yum.repos.d

EOF

}

fi # FUNCTIONS_SOURCED
