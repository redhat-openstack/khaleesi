#!/bin/bash

#ansible host files are not compatible between version 1.x and 2.x
#http://docs.ansible.com/ansible/faq.html#how-do-i-handle-different-machines-needing-different-user-accounts-or-ports-to-log-in-with

usage() { echo "Usage: $0 [from version: -f 1|2] [to version: -t 1|2] [hosts file: -h <string>]" 1>&2; exit 1; }

echo "Convert an ansible hosts file from version 1 -> version 2 or vice versa"
echo ""

while getopts "f:t:h:" o; do
  case "${o}" in
    f)
      ANSIBLE_VERSION_FROM=${OPTARG}
      echo "starting ansible version $ANSIBLE_VERSION_FROM"
      ;;
    t)
      ANSIBLE_VERSION_TO=${OPTARG}
      echo "resulting ansible version $ANSIBLE_VERSION_TO"
      ;;
    h)
      HOSTS_FILE=${OPTARG}
      echo "file name to convert: $HOSTS_FILE"
      ;;
    *)
      usage
      ;;
  esac
done

if [[ $ANSIBLE_VERSION_FROM == 2 ]] && [[ $ANSIBLE_VERSION_TO == 1 ]]; then
  echo "CONVERTING 2 ---> 1"
  sed -i 's/ansible_host/ansible_ssh_host/g' $HOSTS_FILE
  sed -i 's/ansible_user/ansible_ssh_user/g' $HOSTS_FILE
  sed -i 's/ansible_private_key_file/ansible_ssh_private_key_file/g' $HOSTS_FILE
elif [[ $ANSIBLE_VERSION_FROM == 1 ]] && [[ $ANSIBLE_VERSION_TO == 2 ]]; then
  echo "CONVERTING 1 ---> 2"
  sed -i 's/ansible_ssh_host/ansible_host/g' $HOSTS_FILE
  sed -i 's/ansible_ssh_user/ansible_user/g' $HOSTS_FILE
  sed -i 's/ansible_ssh_private_key_file/ansible_private_key_file/g' $HOSTS_FILE
else
  echo "Sorry can not convert ansible version: $ANSIBLE_VERSION_FROM to $ANSIBLE_VERSION_TO"
fi

