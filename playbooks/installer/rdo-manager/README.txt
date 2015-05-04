Sample invocation of ksgen for rdo-manager

khaleesi-settings dev/tkammer

REQUIRES:
in the ansible.cfg
[ssh_connection]
ssh_args = -F ssh.config.ansible


ksgen --config-dir=$CONFIG_BASE/settings generate \
    --provisioner=beaker \
    --provisioner-site=bkr \
    --provisioner-distro=rhel \
    --provisioner-distro-version=7.1 \
    --provisioner-site-user=rdoci-jenkins \
    --provisioner-options=skip_provision \
    --product=rdo \
    --product-version=kilo \
    --product-version-build=last_known_good \
    --product-version-repo=delorean_mgt \
    --product-version-workaround=rhel-7.1 \
    --product-version-images_repo=instack \
    --workarounds=enabled \
    --distro=rhel-7.1 \
    --installer=rdo_manager \
    --installer-env=virthost \
    --installer-topology=minimal_virt \
    --extra-vars product.repo_type_override=rhos-release \
    ksgen_settings.yml
