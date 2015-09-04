# This is the settings file to be used with rdo-manager-test.sh
# Note: only tested running from fedora20+ and rhel7+ requires python2.7

# READ_ME:
# mkdir /tmp/<dir>;
# cp rdo-manager* /tmp/<dir>;
# cd /tmp/<dir>
# change all the lines marked CHANGE_ME with proper values in this file
# check if ssh works to your TESTBED machine with the specified ssh key
# if not, ssh-copy-id root@$TESTBED_IP
# bash -x ./rdo-manager-test.sh


#WORKSPACE=CHANGE_ME                     # base path of git checkouts, e.g. /tmp/<dir>
#CONFIG_BASE=$WORKSPACE/khaleesi-settings
TESTBED_IP=CHANGE_ME                    # hostname or ip of baremetal box
DISTRO=centos                           # [rhel, centos]
PRODUCT=rdo                             # [rdo, rhos]  #rhos is internal only, requires internal khaleesi-settings
PRODUCT_VERSION=kilo                    # [kilo, 7_director] # 7_director is internal only
PRODUCT_VERSION_REPO=delorean_mgt       # [delorean_mgt, puddle]
PRODUCT_VERSION_BUILD=last_known_good   # [last_known_good, latest]
DISTRO_VERSION=7.0                      # atm 7.1 for rhel, 7.0 for centos
INSTALLER_IMAGES=build                  # [build, import] #import only used for puddles
INSTALLER_POST_ACTION=default           # [default, none, scale_up_delete]
INSTALLER_NETWORK_VARIANT=gre           # [gre, ml2-vxlan]
INSTALLER_NETWORK_ISOLATION=none        # [none, single_nic_vlans]
INSTALLER_TEMPEST=api                   # [api, disabled, minimal, scenario, smoke]
YUM_REPO_OVERRIDE=none                  # [rhos-release,rhsm,none] none is used for centos
PRIVATE_KEY=~/.ssh/id_rsa                   # ~/.ssh/id_rsa
KHALEESI_SETTINGS=https://github.com/redhat-openstack/khaleesi-settings.git #internal redhat repo required for rhel
KHALEESI=https://github.com/redhat-openstack/khaleesi.git
#ANSIBLE_SETTINGS=jenkins/ansible_rdo_mang_settings.sh
