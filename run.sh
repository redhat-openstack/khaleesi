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
    local rdo_icehouse_f20_baseurl='http://repos.fedorapeople.org/repos/openstack/openstack-icehouse/fedora-20'
    local rdo_icehouse_epel6_baseurl='http://repos.fedorapeople.org/repos/openstack/openstack-icehouse/epel-6'
    local default_flavor_id=4
    local default_floating_nw_name='external'

    local key_file=${KEY_FILE:-/key.pem }
    local key_name=${SSH_KEY_NAME:-'key'}
    chmod 600 $key_file

    local node_prefix=${NODE_PREFIX:-st}
    local flavor_id=${FLAVOR_ID:-$default_flavor_id}
    local floating_nw_name=${FLOATING_NETWORK_NAME:-$default_floating_nw_name}
    local network_name=${NETWORK_NAME:-'default'}

    local baseurl=${REPO_BASEURL:-$rdo_icehouse_f20_baseurl}
    local image_id=${IMAGE_ID:-'CHANGE_ME'}
    local net_1=${NET_1:-'CHANGE_ME'}
    local net_2=${NET_2:-'CHANGE_ME'}

    local tags=${TAGS:-'--skip-tags workaround'}
    local tempest_tests=${TEMPEST_TEST_NAME:-'tempest'}
    local remote_user=${REMOTE_USER:-'cloud-user'}


cat > settings.yml <<-EOF
# job config

selinux: permissive  #[permissive, enforcing]

config:
  product: rdo
  version: icehouse
  repo: production
  verbosity:
    - info
    - warning
    - debug

# OpenStack controller settings
os_auth_url: '$OS_AUTH_URL'
os_username: $OS_USERNAME
os_password: $OS_PASSWORD
os_tenant_name: $OS_TENANT_NAME

# instance settings
node_prefix: $node_prefix
network_ids: [{ net-id: '$net_1' }, { net-id: '$net_2' } ]
image_id: $image_id
ssh_private_key: $key_file
ssh_key_name: $key_name
flavor_id: $flavor_id
floating_network_name: $floating_nw_name

nodes:
  - name: "{{ node_prefix }}rdopkg"
    image_id: "{{ image_id }}"
    key_name: "{{ ssh_key_name }}"
    flavor_id: "{{ flavor_id }}"
    network_ids: "{{ network_ids }}"
    hostname: packstack.example.com
    groups: "packstack,controller,compute,openstack_nodes"
    packstack_node_hostgroup: packstack

#VM settings
epel_repo: download.fedoraproject.org/pub/epel/6/
gpg_check: 0
ntp_server: clock.redhat.com
reboot_delay: +1

# Currently sudo w/ NOPASSWD must be enabled in /etc/sudoers for sudo to work
# running w/ -u $remote_user and -s will override these options
sudo: yes
remote_user: $remote_user
sudo_user: root

#Packstack config override
provision_tempest: y
provision_demo: y

#See group_vars/* for workaround enable/disable

tempest:
    puppet_file: /tmp/tempest_init.pp
    checkout_dir: /var/lib/tempest
    revision: 'stable/havana'
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

EOF



### disabled since it is already in <git.root>/ansible.cfg
##export ANSIBLE_HOST_KEY_CHECKING=False
##export ANSIBLE_ROLES_PATH=$WORKSPACE/khaleesi/roles
##export ANSIBLE_LIBRARY=$WORKSPACE/khaleesi/library:$VIRTUAL_ENV/share/ansible

ansible-playbook -i local_hosts  \
 playbooks/packstack/rdo_neutron_aio_playbook.yml \
    --extra-vars @settings.yml -v -u $remote_user -s $tags
}

main "$@"
