Sample invocation of ksgen for rdo-manager

khaleesi-settings dev/tkammer

REQUIRES:
in the ansible.cfg
[ssh_connection]
ssh_args = -F ssh.config.ansible

Manual Provisioning requires:
#hosts
[virthost]
10.1.1.1 groups=virthost ansible_ssh_host=10.1.1.1 ansible_ssh_user=stack ansible_ssh_private_key_file=~/.ssh/id_rsa

[local]
localhost ansible_connection=local

#Verify that ansible can ssh to the nodes listed in hosts
ssh root@10.1.1.1 ls -la

#rdo rhel
ksgen --config-dir=$CONFIG_BASE/settings generate \
    --provisioner=manual \
    --product=rdo \
    --product-version=kilo \
    --product-version-build=last_known_good \
    --product-version-repo=delorean_mgt \
    --product-version-workaround=rhel-7.1 \
    --workarounds=enabled \
    --distro=rhel-7.1 \
    --installer=rdo_manager \
    --installer-env=virthost \
    --installer-topology=minimal_virt \
    --extra-vars product.repo_type_override=rhos-release \
    ksgen_settings.yml

#osp puddle
ksgen --config-dir=$CONFIG_BASE/settings generate \
    --provisioner=manual \
    --product=rhos \
    --product-version=7_director \
    --product-version-repo=puddle \
    --distro=rhel-7.1 \
    --installer=rdo_manager \
    --installer-env=virthost \
    --installer-topology=minimal_virt \
    --extra-vars product.repo_type_override=none \
    ksgen_settings.yml

#osp poodle
ksgen --config-dir=$CONFIG_BASE/settings generate \
    --provisioner=manual
    --product=rhos \
    --product-version=7_director \
    --product-version-repo=poodle \
    --distro=rhel-7.1 \
    --installer=rdo_manager \
    --installer-env=virthost \
    --installer-topology=minimal_virt \
    --extra-vars product.repo_type_override=none \
    ksgen_settings.yml
