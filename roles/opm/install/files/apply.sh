#!/bin/bash

puppet apply --detailed-exitcodes --modulepath=/usr/share/openstack-puppet/modules $1

exit_code=$?

if [ $exit_code -gt 2 ]; then
  echo "ERROR: puppet apply returned with $exit_code exit code."
  exit 1
fi
