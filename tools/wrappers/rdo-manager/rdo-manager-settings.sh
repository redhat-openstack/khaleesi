# This is the settings file to be used with rdo-manager-test.sh
# Note: only tested running from fedora20+

# READ_ME:
# mkdir /tmp/empty_dir;
# cp rdo-manager* /tmp/empty_dir;
# cd /tmp/empty_dir
# change all the lines marked CHANGE_ME with proper values in this file
# check if ssh works to your TESTBED machine with the specified ssh key
# if not, ssh-copy-id root@$TESTBED_IP
# bash -x ./rdo-manager-test.sh


WORKSPACE=CHANGE_ME #base path of git checkouts, e.g. /tmp/empty_dir
TESTBED_IP=CHANGE_ME #hostname or ip of baremetal box
CONFIG_BASE=$WORKSPACE/khaleesi-settings
TEST_COMPONENT=instack-undercloud
TEST_COMPONENT_URL=https://github.com/rdo-management/instack-undercloud.git
PROVISION_OPTION=skip_provision  #[skip_provision, execute_provision] for baremetal box
DISTRO=rhel-7.1
PRIVATE_KEY=CHANGE_ME  # ~/.ssh/id_rsa
KHALEESI_SETTINGS=CHANGE_ME #git url to khaleesi-settings internal only atm.
KHALEESI=https://github.com/redhat-openstack/khaleesi.git
ANSIBLE_SETTINGS=jenkins/ansible_rdo_mang_settings.sh
