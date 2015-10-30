See http://khaleesi.readthedocs.org/en/master/cookbook.html for a quickstart

To *only* cleanup a virthost:
ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/installer/rdo-manager/cleanup_virthost.yml

To *only* install the undercloud:
ansible-playbook -vv --extra-vars @ksgen_settings.yml -i local_hosts playbooks/installer/rdo-manager/install_undercloud.yml

To *only* deploy the overcloud
ansible-playbook -vv --extra-vars @ksgen_settings.yml -i hosts playbooks/installer/rdo-manager/overcloud/main.yml
