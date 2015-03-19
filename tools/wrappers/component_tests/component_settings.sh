#settings file to be used with component_test.sh
#source this file then copy component_test.sh to $WORKSPACE and execute
WORKSPACE=CHANGE_ME #base path of git checkouts
CONFIG_BASE=$WORKSPACE/khaleesi-settings
TEST_COMPONENT=nova
TEST_COMPONENT_URL=git://CHANGE_ME/nova.git
PROVISION_OPTION=skip_provision  #[skip_provision, execute_provision]
DISTRO=rhel-7.0
TESTBED_IP=CHANGE_ME
TESTBED_USER=CHANGE_ME #(if cloud image use default cloud image id)
PRIVATE_KEY=CHANGE_ME
KHALEESI_SETTINGS=http://CHANGE_ME/git/khaleesi-settings.git
KHALEESI=https://github.com/redhat-openstack/khaleesi.git
ANSIBLE_SETTINGS=packstack/jenkins/ansible_settings.sh
