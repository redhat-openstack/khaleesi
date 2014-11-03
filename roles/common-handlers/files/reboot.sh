#!/bin/bash
set -e

function get_distribution() {
 local release=""
 local release_string="$(cat /etc/redhat-release)"
 if [[ "${release_string}" == *Fedora* ]]; then release="Fedora"
 elif [[ "${release_string}" == *Red* ]]; then release="RedHat"
 elif [[ "${release_string}" == *CentOS* ]]; then release="CentOS"
 else
   echo ERROR: unable to determine distribution 1>&2
   exit 1;
 fi
 echo $release
}

function get_release() {
 local version="$(cat /etc/redhat-release | awk '{print $(NF-1) }')"
 if [[ "${version}" == *Beta* ]]; then
   version="$(cat /etc/redhat-release | awk '{print $(NF-2) }')"
 elif [[ ${version%.*} -gt 0 ]]; then
   version=${version%.*}
 elif [[ ${version%.*.*} -gt 0 ]]; then #for CentOS-7+
   version=${version%.*.*}
 else
   echo ERROR: unable to determine distribution, got $version 1>&2
   exit 1;
 fi
 echo $version
}

DISTRIBUTION=$(get_distribution)
if [[ $DISTRIBUTION != "Fedora" ]]; then
  RELEASE=$(get_release)
fi
echo DISTRIBUTION=$DISTRIBUTION
echo RELEASE=$RELEASE

if [[ $DISTRIBUTION == "Fedora" ]]; then
  command="/sbin/shutdown -r +1 --no-wall"
elif [ $DISTRIBUTION == "RedHat" ] && [[ $RELEASE -lt 7 ]]; then
  command="/sbin/shutdown -r +1 "
elif [ $DISTRIBUTION == "CentOS" ] && [[ $RELEASE -lt 7 ]]; then
  command="/sbin/shutdown -r +1 "
elif [ $DISTRIBUTION == "RedHat" ] && [[ $RELEASE -ge 7 ]]; then
  command="/sbin/shutdown -r +1 --no-wall"
elif [ $DISTRIBUTION == "CentOS" ] && [[ $RELEASE -ge 7 ]]; then
  command="/sbin/shutdown -r +1 --no-wall"
else
  exit 1
fi

echo $command
$command
