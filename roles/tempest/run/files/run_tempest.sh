#!/usr/bin/env bash
set -e -u

usage() {
    echo "$(basename $0) tempest_dir --exclude-file [file1, file2, ...] --exclude-tests test1..."
}


tempest.testr() {
    echo "Running testr ... "
    local skip_list=${!1:-}
    skip_list+=" "${!2:-}
    echo "Skipping tests: $skip_list"

    local is_empty=$(tr -d [[:blank:]] <<< $skip_list)
    if [[ -z $is_empty ]] ; then
        prevent_empty_list="####---prevent skip grep options to be empty-- it will match everything and skip all otherwise---###"
    fi

    local grep_skip_options="\\("$(sed -e 's|\ |\\\||g' <<< $skip_list)"\\)"
    local include_list="smoke"

    testr init
    testr run --parallel --subunit \
              --load-list=<(testr list-tests $include_list |\
                          tail -n +5 |\
                          grep -v "$prevent_empty_list$grep_skip_options") |
        tee >( subunit2junitxml --output-to=nosetests.xml ) |
        subunit-2to1 | tee run.log |
        tools/colorizer.py
    return 0
}

tempest.testr_single() {
    echo "Running testr ... "
    local tempest_test_name=${1:-""}

    testr init
    testr run --subunit $tempest_test_name |
        tee >( subunit2junitxml --output-to=nosetests.xml ) |
        subunit-2to1 | tee run.log |
        tools/colorizer.py
    return 0
}

tempest.tox() {
    echo "Running tox ... "
    local skip_list=${!1:-}
    skip_list+=" "${!2:-}
    echo "Skipping tests: $skip_list"

    local is_empty=$(tr -d [[:blank:]] <<< $skip_list)
    if [[ -z $is_empty ]] ; then
        prevent_empty_list="####---prevent skip grep options to be empty-- it will match everything and skip all otherwise---###"
    fi

    local grep_skip_options="\\("$(sed -e 's|\ |\\\||g' <<< $skip_list)"\\)"
    local include_list="smoke"

    tox -- --parallel --subunit \
              --load-list=<(testr list-tests $include_list |\
                          tail -n +5 |\
                          grep -v "$prevent_empty_list$grep_skip_options") |
        tee >( subunit2junitxml --output-to=nosetests.xml ) |
        subunit-2to1 | tee run.log |
        tools/colorizer.py
    return 0
}

tempest.tox_single() {
    echo "Running testr ... "
    local tempest_test_name=${1:-""}

    tox -- --subunit $tempest_test_name |
        tee >( subunit2junitxml --output-to=nosetests.xml ) |
        subunit-2to1 | tee run.log |
        tools/colorizer.py
    return 0
}

tempest.run_smoketest() {
    local tempest_dir=$1; shift
    local tempest_test_name=${1:-""}; shift

    if [[ $1 != '--exclude-files' ]]; then
        usage
        return 1
    fi
    shift       ## skip --exclude-files
    local args="$@"

    # files first, so parts before --exclude-tests
    local -a exclude_files=( $(echo ${args[@]} |
                 awk -F'--exclude-tests' '{ print $1 }' |
                 tr -d ',' | tr -d '[' | tr -d ']') )
    local -a exclude_tests=( $(echo ${args[@]} |
                awk -F'--exclude-tests' '{ print $2 }' |
                 tr -d ',' | tr -d '[' | tr -d ']') )

    cd $tempest_dir

    # HACK to disable virtual-env unset VAR error {
    test -r  .venv/bin/activate && {
        set +u
        source .venv/bin/activate
        set -u
    }
    # }

    local py_version=$(python --version 2>&1)

    if [[ $py_version =~ "2.7" &&  -z $tempest_test_name ]]; then
        tempest.testr  exclude_files[@] exclude_tests[@]
    elif [[ $tempest_test_name == "none" ]]; then
        echo "Skipping tempest"
        return 0
    elif [[ $tempest_test_name == "all" ]]; then #same as first option
        tempest.testr  exclude_files[@] exclude_tests[@]
    elif [[ $py_version =~ "2.7" &&  -n $tempest_test_name ]]; then
        tempest.testr_single $tempest_test_name
    else
        echo "Please check test variables"
        return 1
    fi

    ### NOTE: test if the nosetests.xml exist in that case we don't treat the
    ### tempest run as a failure, rather let the xunit deal with the
    ### interpreting the nosetests.xml
    test -f nosetests.xml
    return $?
}

tempest.run_smoketest "$@"

