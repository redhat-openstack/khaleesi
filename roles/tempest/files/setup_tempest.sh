#!/usr/bin/env bash
set -e -u

main() {
    local tempest_init_pp=$1; shift
    local tempest_dir=$1; shift

    # make a back up the original tempest directory
    mv -f $tempest_dir $tempest_dir.orig 2>/dev/null || true

    # $::identity_uri
    source /root/keystonerc_admin
    local keystone_service_id=$(keystone service-list |
                grep keystone | awk '{print $2}')
    export FACTER_IDENTITY_URI=$(keystone endpoint-list |
                grep $keystone_service_id | awk '{print $6}')

    source /root/keystonerc_demo
    # $::image_ref,
    export FACTER_IMAGE_REF=$(glance index | grep cirros | awk '{print $1}' | head -n1 )
    # $::image_ref_alt,
    export FACTER_IMAGE_REF_ALT=$(glance index | grep cirros | awk '{print $1}' | head -n1 )
    # $::public_network_id,
    export FACTER_PUBLIC_NETWORK_ID=$(neutron net-list | grep public | awk '{print $2}' | head -n1 )

    #list variables and apply puppet module
    facter | grep -E "image_|public_network|identity"


    local puppet_modules_dir=$(rpm -ql packstack-modules-puppet | grep 'modules$')
    if [[  -z $puppet_modules_dir ]]; then
        local puppet_modules_dir=$(rpm -ql openstack-packstack | grep 'modules$' | tail -n 1)
    else
        return 1
    fi
    puppet apply --modulepath=$puppet_modules_dir $tempest_init_pp
    return $?
}

main "$@"

