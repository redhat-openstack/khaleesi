#!/usr/bin/env bash
set -e -u

usage() {
    echo "$(basename $0) tempest_dir --exclude-file [file1, file2, ...] --exclude-tests test1..."
}


tempest.nose_test() {
    local -a exclude_files=(${!1:-})
    local -a exclude_tests=(${!2:-})

    local x
    local -a nose_exclude_files=()
    test ${#exclude_files[@]} -ne 0 &&
        for x in "${exclude_files[@]}"; do
            nose_exclude_files+=( --ignore-files=$x )
        done

    local -a nose_exclude_tests=()
    test ${#exclude_tests[@]} -ne 0 &&
        for x in "${exclude_tests[@]}"; do
            nose_exclude_tests+=( --exclude=$x )
        done

    export NOSE_WITH_OPENSTACK=1
    export NOSE_OPENSTACK_COLOR=1
    export NOSE_OPENSTACK_RED=15.00
    export NOSE_OPENSTACK_YELLOW=3.00
    export NOSE_OPENSTACK_SHOW_ELAPSED=1
    export NOSE_OPENSTACK_STDOUT=1
    export TEMPEST_PY26_NOSE_COMPAT=1

    echo nosetests --verbose --attr=type=smoke  --with-xunit \
        ${nose_exclude_files[@]} ${nose_exclude_tests[@]} \
        tempest

    nosetests --verbose --attr=type=smoke  --with-xunit \
        ${nose_exclude_files[@]} ${nose_exclude_tests[@]} \
        tempest || true
    return 0
}

tempest.nose_test_single() {
    local tempest_test_name=${1:-""}
 
    export NOSE_WITH_OPENSTACK=1
    export NOSE_OPENSTACK_COLOR=1
    export NOSE_OPENSTACK_RED=15.00
    export NOSE_OPENSTACK_YELLOW=3.00
    export NOSE_OPENSTACK_SHOW_ELAPSED=1
    export NOSE_OPENSTACK_STDOUT=1
    export TEMPEST_PY26_NOSE_COMPAT=1

    echo nosetests --verbose --attr=type=smoke  --with-xunit \
        $tempest_test_name

    nosetests --verbose --attr=type=smoke  --with-xunit \
        $tempest_test_name || true
    return 0
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
    testr run $tempest_test_name |
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
        set +u
        source .venv/bin/activate
        set -u
    # }

    local py_version=$(python --version 2>&1)

    #tests.scenario.test_network_basic_ops works w/ nosetest
    # on python2.6/7 where testr does not. 
    # moving this to only use nosetest atm.
    if [[ $py_version =~ "2.6" &&  -z $tempest_test_name ]]; then
        tempest.nose_test  exclude_files[@] exclude_tests[@]
    elif [[ $py_version =~ "2.7" &&  -z $tempest_test_name ]]; then
        tempest.nose_test  exclude_files[@] exclude_tests[@]
    elif [[ $py_version =~ "2.6" &&  -n $tempest_test_name ]]; then
        tempest.nose_test_single $tempest_test_name
    elif [[ $py_version =~ "2.7" &&  -n $tempest_test_name ]]; then
        tempest.nose_test_single $tempest_test_name
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

