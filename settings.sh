#! /usr/bin/env bash
set -e -u

# Quick Instructions:
# export:
# IMAGE_ID to the id of the image
#
# Two networks are not required, but one is atm. "neutron net-list"
# export:
# NET_1
# NET_2
#
# KEY_FILE= full path to openstack private ssh key for instance
# SSH_KEY_NAME= name of ssh key in openstack
#
# TAGS='--tags=provision,prep'
# REMOTE_USER= [cloud-user,fedora]
#

main() {
    local default_flavor_id=4
    local default_tempest_flavor_id=2
    local default_floating_nw_name='external'
    local wait_for_boot=${WAIT_FOR_BOOT:-'180'}

    local key_file=${KEY_FILE:-/key.pem }
    local key_name=${SSH_KEY_NAME:-'key'}
    chmod 600 $key_file

    local job_name=${JOB_NAME}
    local flavor_id=${FLAVOR_ID:-$default_flavor_id}
    local floating_nw_name=${FLOATING_NETWORK_NAME:-'external'}
    local network_name=${NETWORK_NAME:-'default'}

    local image_id=$IMAGE_ID
    local tempest_image_id=$TEMPEST_IMAGE_ID
    local tempest_flavor_id=${TEMPEST_FLAVOR_ID:-$default_tempest_flavor_id}
    local net_1=${NET_1:-'CHANGE_ME'}
    local net_2=${NET_2:-''}
    local net_2_name=${NET_2_NAME:-'packstack_int'}
    local net_3=${NET_3:-''}
    local net_3_name=${NET_3_NAME:-'foreman_ext'}

    export tags=${TAGS:-''}
    export skip_tags=${SKIP_TAGS:-''}
    local tempest_tests=${TEMPEST_TEST_NAME:-'tempest.scenario.test_network_basic_ops'}
    export remote_user=${REMOTE_USER:-'cloud-user'}
    export tempest_branch=${TEMPEST_BRANCH:-'stable/havana'}
    local tempest_remote_user=${TEMPEST_REMOTE_USER:-'fedora'}

    local rhel_os_repo=${RHEL_OS_REPO:-''}
    local rhel_updates_repo=${RHEL_UPDATES_REPO:-''}
    local rhel_optional_repo=${RHEL_OPTIONAL_REPO:-''}

    local sm_username=${SM_USERNAME:-''}
    local sm_password=${SM_PASSWORD:-''}

    local host_env=${HOST_ENV:-'neutron'}
    local product=${PRODUCT:-'rdo'} #product
    local productrelease=${PRODUCTRELEASE:-'icehouse'} #rdo_release
    local productreleaserepo=${PRODUCTRELEASEREPO:-'production'} #rdo_repo
    local netplugin=${NETPLUGIN:-'neutron'} #network_driver
    local selinux=${SELINUX:-'enforcing'} #enforcing, permissive

    local update_rpms_tarball=${UPDATE_RPMS_TARBALL:-''}

    local net_ids="[{ net-id: '$net_1' }"
    if [[ ! -z $net_2 ]]; then
      net_ids="$net_ids, { net-id: '$net_2' }"
    fi
    if [[ ! -z $net_3 ]]; then
      net_ids="$net_ids, { net-id: '$net_3' }"
    fi
    net_ids="$net_ids ]"

cat > settings.yml <<-EOF
# job config

selinux: $selinux
packstack_int: whayutin

config:
  product: $product
  version: $productrelease
  repo: $productreleaserepo
  netplugin: $netplugin
  host_env: $host_env
  verbosity:
    - info

# OpenStack controller settings, can be set by sourcing a keystonerc file
os_auth_url: '$OS_AUTH_URL'
os_username: $OS_USERNAME
os_password: $OS_PASSWORD
os_tenant_name: $OS_TENANT_NAME

# instance settings
job_name: $job_name
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
    puppet_file: /tmp/tempest_init.pp
    checkout_dir: /var/lib/tempest
    revision: $tempest_branch
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
  - /root/packstack*
  - /var/lib/tempest/*
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

main "$@"
