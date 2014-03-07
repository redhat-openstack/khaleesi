#! /usr/bin/env bash
set -e -u
main() {

playbook=${1:-'aio.yml'}
# If the playbook does NOT contain a '/', default to the packstack playbooks
if [[ $(expr index "$playbook" /) -eq 0 ]]; then
  playbook="playbooks/packstack/$playbook"
fi
echo $playbook


source settings.sh

cmdline="ansible-playbook -i local_hosts $playbook --extra-vars @settings.yml "
if [[ ! -e repo_settings.yml && ! -e job_settings.yml ]]; then
  echo "settings = settings.yml"
  cmdline="$cmdline \
        --extra-vars @nodes.yml"
elif [[ ! -e repo_settings.yml && -e job_settings.yml ]]; then
  echo "settings = settings.yml, job_settings.yml"
  cmdline="$cmdline \
        --extra-vars @job_settings.yml  \
          --extra-vars @nodes.yml"
elif [[ ! -e job_settings.yml && -e repo_settings.yml ]]; then
  echo "settings = settings.yml, repo_settings.yml"
  cmdline="$cmdline \
        --extra-vars @nodes.yml  \
          --extra-vars @repo_settings.yml"
elif [[ -e job_settings.yml && -e repo_settings.yml ]]; then
  echo "settings = settings.yml, repo_settings.yml, job_settings.yml"
  cmdline="$cmdline \
        --extra-vars @repo_settings.yml \
          --extra-vars @job_settings.yml \
            --extra-vars @nodes.yml"
fi

if [[ ! -z $remote_user ]]; then
  cmdline="$cmdline -u $remote_user -s"
fi

if [[ ! -z $tags ]]; then
  # Remove extraneous '--tags' first. Jobs that use this should switch to just
  # providing the tags
  tags=${tags#--tags=}
  cmdline="$cmdline --tags $tags"
fi

if [[ ! -z $skip_tags ]]; then
  # Same as tags
  skip_tags=${skip_tags#--skip_tags}
  cmdline="$cmdline --skip-tags $skip_tags"
fi

echo "Execute Command:"
echo "$cmdline"
$cmdline

#need a zero exit everytime so teardown can be executed
return 0
}

collect_logs() {
  ansible-playbook -i local_hosts  \
    playbooks/collect_logs.yml \
      --extra-vars @settings.yml  \
        --extra-vars @nodes.yml  \
        -u $remote_user -s
}

if [ ! -e nodes.yml ]; then
  echo "Please create a nodes.yml file to define your environment"
  echo "See https://github.com/redhat-openstack/khaleesi/blob/master/doc/packstack.md"
  exit 1
fi

# requires a 0 exit code for clean.sh to execute
main "$@" || true
collect_logs || true

