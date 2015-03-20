# This is the settings file to be used with packstack-test.sh
# Note: only tested running from fedora20+

# READ_ME:
# mkdir /tmp/empty_dir;
# cp packstack* /tmp/empty_dir;
# ensure any value marked CHANGE_ME is updated
# source this file execute packstack-test.sh


WORKSPACE=CHANGE_ME #base path of git checkouts, e.g. /tmp/empty_dir
TESTBED_USER=cloud-user  #don't use root here, [cloud-user, fedora, centos]
CONFIG_BASE=$WORKSPACE/khaleesi-settings
PROVISION_OPTION=execute_provision  #[skip_provision, execute_provision] for baremetal box
DISTRO=rhel-7.1  #[rhel-7.1 (internal only), centos-7.0, fedora-21 ]
PRIVATE_KEY=CHANGE_ME  # ~/.ssh/id_rsa  (key used to ssh to instance )
KHALEESI_SETTINGS=https://github.com/redhat-openstack/khaleesi-settings.git #git url to khaleesi-settings, --> if internal see engineering git <--
KHALEESI=https://github.com/redhat-openstack/khaleesi.git
ANSIBLE_SETTINGS=packstack/jenkins/ansible_settings.sh
