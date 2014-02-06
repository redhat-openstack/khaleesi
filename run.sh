#! /usr/bin/env bash
set -e -u
main() {

source settings.sh

ansible-playbook -i local_hosts  \
 playbooks/packstack/rdo_neutron_aio_playbook.yml \
    --extra-vars @settings.yml -v -u $remote_user -s $tags
}

main "$@"
