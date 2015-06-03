ksgen --config-dir=$CONFIG_BASE/settings generate \
      --provisioner=openstack \
      --provisioner-site=qeos \
      --provisioner-site-user=rhos-jenkins \
      --extra-vars provisioner.key_file=$PRIVATE_KEY \
      --provisioner-options=execute_provision \
      --product=rhos \
      --product-version=6.0 \
      --distro=rhel-7.0 \
      --tester-component=nova \
      --tester=unittest \
      ksgen_settings.yml
