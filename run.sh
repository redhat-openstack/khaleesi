#! /usr/bin/env bash
set -e -u
main() {

source settings.sh

if [ ! -e repo_settings.yml ]; then
  echo "settings = settings.yml"
  ansible-playbook -i local_hosts  \
    playbooks/packstack/rdo_neutron_aio.yml \
      --extra-vars @settings.yml  \
        -v -u $remote_user -s $tags
elif [[ ! -e job_settings.yml && -e repo_settings.yml ]]; then
  echo "settings = settings.yml, repo_settings.yml"
  ansible-playbook -i local_hosts  \
    playbooks/packstack/rdo_neutron_aio.yml \
      --extra-vars @settings.yml --extra-vars @repo_settings.yml \
         -v -u $remote_user -s $tags
elif [[ -e job_settings.yml && -e repo_settings.yml ]]; then
  echo "settings = settings.yml, repo_settings.yml, job_settings.yml"
  ansible-playbook -i local_hosts  \
    playbooks/packstack/rdo_neutron_aio.yml \
      --extra-vars @settings.yml \
        --extra-vars @repo_settings.yml \
          --extra-vars @job_settings.yml \
             -v -u $remote_user -s $tags
fi
#need a zero exit everytime so teardown can be executed
return 0
}

collect_logs() {
  ansible-playbook -i local_hosts  \
    playbooks/collect_logs.yml \
      --extra-vars @settings.yml  \
        -v -u $remote_user -s
}

#require a 0 exit code for clean.sh to execute
main "$@" || true
collect_logs

