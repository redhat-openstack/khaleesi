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
            nose_exclude_files+=( --ignore-files="'"$x"'" )
        done

    local -a nose_exclude_tests=()
    test ${#exclude_tests[@]} -ne 0 &&
        for x in "${exclude_tests[@]}"; do
            nose_exclude_tests+=( --exclude="'"$x"'" )
        done

    export NOSE_WITH_OPENSTACK=1
    export NOSE_OPENSTACK_COLOR=1
    export NOSE_OPENSTACK_RED=15.00
    export NOSE_OPENSTACK_YELLOW=3.00
    export NOSE_OPENSTACK_SHOW_ELAPSED=1
    export NOSE_OPENSTACK_STDOUT=1
    export TEMPEST_PY26_NOSE_COMPAT=1

    nosetests --verbose --attr=type=smoke  --with-xunit \
        ${nose_exclude_files[@]} ${nose_exclude_tests[@]} \
        tempest
}

tempest.testr() {
    echo "Running testr ... "
    testr init
    testr run --parallel --subunit smoke |
        tee >( subunit2junitxml --output-to=nosetests.xml ) |
        subunit-2to1 | tee run.log |
        tools/colorizer.py
}

tempest.run_smoketest() {
    echo $#  $@
    local tempest_dir=$1; shift

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
    if [[ $py_version =~ "2.6" ]]; then
        tempest.nose_test  exclude_files[@] exclude_tests[@]
    else
        tempest.testr  exclude_files[@] exclude_tests[@]
    fi

    ### NOTE: test if the nosetests.xml exist in that case we don't treat the
    ### tempest run as a failure, rather let the xunit deal with the
    ### interpreting the nosetests.xml
    test -f nosetests.xml
    return $?
}

tempest.run_smoketest "$@"

