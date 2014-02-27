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
    local default_floating_nw_name='external'

    local key_file=${KEY_FILE:-/key.pem }
    local key_name=${SSH_KEY_NAME:-'key'}
    chmod 600 $key_file

    local node_prefix=${NODE_PREFIX:-st}
    local flavor_id=${FLAVOR_ID:-$default_flavor_id}
    local floating_nw_name=${FLOATING_NETWORK_NAME:-'external'}
    local network_name=${NETWORK_NAME:-'default'}

    local image_id=${IMAGE_ID:-'CHANGE_ME'}
    local net_1=${NET_1:-'CHANGE_ME'}
    local net_2=${NET_2:-'CHANGE_ME'}
    local net_2_name=${NET_2_NAME:-'packstack_int'}

    export tags=${TAGS:-'--skip-tags workaround'}
    local tempest_tests=${TEMPEST_TEST_NAME:-'tempest.scenario.test_network_basic_ops'}
    export remote_user=${REMOTE_USER:-'cloud-user'}

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
    - warning
    - debug

# OpenStack controller settings, can be set by sourcing a keystonerc file
os_auth_url: '$OS_AUTH_URL'
os_username: $OS_USERNAME
os_password: $OS_PASSWORD
os_tenant_name: $OS_TENANT_NAME

# instance settings
node_prefix: $node_prefix
network_ids: [{ net-id: '$net_1' }, { net-id: '$net_2' } ]
net_2_name: $net_2_name
image_id: $image_id
ssh_private_key: $key_file
ssh_key_name: $key_name
flavor_id: $flavor_id
floating_network_name: $floating_nw_name
sm_username: $sm_username
sm_password: $sm_password

cleanup_nodes: "{{ nodes }}"

#VM settings
epel_repo: download.fedoraproject.org/pub/epel/6/
gpg_check: 0
ntp_server: clock.redhat.com
reboot_delay: +1

update_rpms_tarball: $update_rpms_tarball

# Currently sudo w/ NOPASSWD must be enabled in /etc/sudoers for sudo to work
# running w/ -u $remote_user and -s will override these options
remote_user: $remote_user

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
