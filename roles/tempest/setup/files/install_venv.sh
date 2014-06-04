#!/usr/bin/env bash
set -e -u

main() {
    local tempest_dir=$1; shift

    echo "Setting up Virtual env"
    cd $tempest_dir
    rm -rf .venv
    python tools/install_venv.py 1>/dev/null 2>&1 || {
        echo " ... failed, retrying ..."
        python tools/install_venv.py 1>/dev/null 2>&1
    } || {
        echo " ... failed, retrying ..."
        python tools/install_venv.py 1>/dev/null 2>&1
    } || {
        echo " ... failed, retrying ..."
        python tools/install_venv.py
    } || {
        echo "Virtual Env setup failed after 4 retries, quiting"
        return 1
    }
    echo "Virtual Env setup - complete"
}

main "$@"

