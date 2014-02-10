#! /usr/bin/env bash
set -e -u
main() {

source settings.sh

ansible-playbook -i local_hosts  \
 playbooks/packstack/rdo_neutron_aio.yml \
    --extra-vars @settings.yml --extra-vars @repo_settings.yml \
       -v -u $remote_user -s $tags
}

main "$@"
