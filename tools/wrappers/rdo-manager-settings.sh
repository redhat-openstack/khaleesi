#settings file to be used with component_test.sh
#source this file then copy component_test.sh to $WORKSPACE and execute
WORKSPACE=CHANGE_ME #base path of git checkouts
TESTBED_IP=CHANGE_ME #hostname or ip of baremetal box
TESTBED_USER=stack  #don't use root here
CONFIG_BASE=$WORKSPACE/khaleesi-settings
TEST_COMPONENT=instack-undercloud
TEST_COMPONENT_URL=git@github.com:rdo-management/instack-undercloud.git
PROVISION_OPTION=skip_provision  #[skip_provision, execute_provision] for baremetal box
DISTRO=rhel-7.1
PRIVATE_KEY=CHANGE_ME
KHALEESI_SETTINGS=CHANGE_ME
KHALEESI=https://github.com/redhat-openstack/khaleesi.git
ANSIBLE_SETTINGS=packstack/jenkins/ansible_settings.sh
