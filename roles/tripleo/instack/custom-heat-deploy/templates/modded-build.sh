#!/bin/bash

set -eux
set -o pipefail

export image_build=${1:-"all"}

export INSTACK_ROOT=${INSTACK_ROOT:-"/usr/share"}
export ELEMENTS_PATH=${ELEMENTS_PATH:-"/usr/share/tripleo-image-elements:/usr/share/instack-undercloud:/usr/share/openstack-heat-templates/software-config/elements"}
source "$INSTACK_ROOT"/instack-undercloud/instack-sourcerc

# Override TMP_DIR for image build.
# It defaults /tmp. But, /tmp is usually tmpfs mounted on Fedora, and dib will
# use a tmpfs on it's own if there is enough free RAM.
export TMP_DIR=${TMP_DIR:-/var/tmp}

export NODE_ARCH=${NODE_ARCH:-amd64}
# TODO(bnemec): This should use set-os-type from tripleo-incubator, but that's
# currently broken for rhel7.
if $(grep -Eqs 'Red Hat Enterprise Linux Server release 7' /etc/redhat-release); then
    DEFAULT_DIST=rhel7
else
    DEFAULT_DIST=fedora
fi
export NODE_DIST=${NODE_DIST:-$DEFAULT_DIST}
export DEPLOY_IMAGE_ELEMENT=${DEPLOY_IMAGE_ELEMENT:-deploy-ironic}
export DEPLOY_NAME=${DEPLOY_NAME:-deploy-ramdisk-ironic}
export DISCOVERY_IMAGE_ELEMENT=${DISCOVERY_IMAGE_ELEMENT:-discovery-ironic}
export DISCOVERY_NAME=${DISCOVERY_NAME:-discovery-ramdisk}

export DIB_COMMON_ELEMENTS=${DIB_COMMON_ELEMENTS:-""}
export DIB_COMMON_ELEMENTS="$DIB_COMMON_ELEMENTS \
baremetal \
base \
element-manifest \
network-gateway \
os-collect-config \
os-refresh-config \
os-apply-config \
heat-config-ansible \
heat-config-cfn-init \
heat-config-puppet \
heat-config-salt \
heat-config-script"

export RHOS=${RHOS:-"0"}
export RHOS_RELEASE=${RHOS_RELEASE:-"0"}
if [[ "rhel7 centos7" =~ "$NODE_DIST" ]]; then
    # Default filesystem type is XFS for RHEL 7
    export FS_TYPE=${FS_TYPE:-xfs}

    if [ "$RHOS" = "0" ]; then
        export DIB_COMMON_ELEMENTS="$DIB_COMMON_ELEMENTS epel rdo-juno rdo-release"
    elif [ ! "$RHOS_RELEASE" = "0" ]; then
        export DIB_COMMON_ELEMENTS="$DIB_COMMON_ELEMENTS rhos-release"
    fi
fi

function vanilla {
    if [ ! -f vanilla.qcow2 ]; then
        disk-image-create \
            -a $NODE_ARCH \
            -o vanilla \
            $NODE_DIST \
            $DIB_COMMON_ELEMENTS \
            2>&1 | tee vanilla.log
    fi
}

if [ "$image_build" = "all" ]; then
    vanilla
else
    eval "$image_build"
fi
