#settings file to be used with component_test.sh
#source this file then copy component_test.sh to $WORKSPACE and execute
CONFIG_BASE=$WORKSPACE/khaleesi-settings
DISTRO=rhel-7.1
KHALEESI=https://github.com/redhat-openstack/khaleesi.git
KHALEESI_SETTINGS=http://###CHANGE_ME###/gerrit/khaleesi-settings.git
PRODUCT_REPO=poodle
PRODUCT_TYPE=rhos
PRODUCT_VERSION=7.0
PROVISIONER=openstack
SITE=###CHANGE_ME###
TENANT=rhos-jenkins
TEST_COMPONENT_BRANCH=###CHANGE_ME###
TEST_COMPONENT=neutron
TEST_COMPONENT_URL=http://###CHANGE_ME###/gerrit/neutron.git
TESTER_TYPE=pep8
