#!/bin/bash

if [[ "$1" != "locked" ]]; then
	if [[ ! -z "$1" ]]; then
		# blocking mode, which also executes xtra 'coverage <$1-action>' (like html or report)
		flock /coverage/collect.lock "$0" locked "$1"
	else
		flock --nonblock /coverage/collect.lock "$0" locked
	fi
	exit
fi

# move data files
min_time='-mmin +1'
[[ ! -z "$2" ]] && min_time="" # all files in case of blocking for report
find /coverage -maxdepth 1 $min_time -name data.\* -exec mv {} /coverage/combined/ \;

# ensure we have config for combined/ dir and it will be used for this run
if [[ ! -f config ]]; then
	sed -r 's/^(data_file = .*)$/data_file = \/coverage\/combined\/data/' /coverage/config > /coverage/combined/config
fi
export COVERAGE_FILE=/coverage/combined/data
export COVERAGE_PROCESS_START=/coverage/combined/config
export REPORT_MODE=1

cd /coverage/combined
coverage combine --rcfile=/coverage/combined/config

[[ ! -z "$2" ]] && coverage $2 --rcfile=/coverage/combined/config
