#! /usr/bin/env bash
set -e -u

main() {
    # try installing lvm-libs if it fails, downgrade
    # remove the libs after installation so that packstack
    # can install it

    yum install -y lvm2-libs || {
        yum downgrade -y device-mapper device-mapper-libs
    }
    yum remove -y lvm2-libs
}

main "$@"

