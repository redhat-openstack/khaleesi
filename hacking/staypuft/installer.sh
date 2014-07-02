#! /usr/bin/env bash
set -eu


random_true_false() {
    # Generate binary choice, that is, "true" or "false" value.
    return $(($RANDOM>>14))
}

answer() {
    local ans
    read ans
    echo "$@: $ans" >> answer.txt
}

print_settings_change() {
    echo Networking setup:
    echo        Network interface: 'virbr0'
    echo               IP address: '192.168.100.1'
    echo             Network mask: '255.255.255.0'
    echo          Network address: '192.168.100.0'
    echo             Host Gateway: '10.16.71.254'
    echo         DHCP range start: '192.168.100.2'
    echo           DHCP range end: '192.168.100.254'
    echo             DHCP Gateway: '192.168.100.1'
    echo            DNS forwarder: '192.168.100.1'
    echo                   Domain: 'rhts.eng.bos.redhat.com'
    echo              Foreman URL: 'https://hp-bl660cgen8-01.rhts.eng.bos.redhat.com'
    echo            NTP sync host: '0.rhel.pool.ntp.org'
    echo Configure networking on this machine: ✓
    echo Configure firewall on this machine: ✓
    echo
    echo "Staypuft can configure the networking and firewall rules on this machine with the above configuration. Defaults are populated from the this machine's existing networking configuration."
    echo
    echo If you DO NOT want Staypuft Installer to configure networking please set 'Configure networking on this machine' to No before proceeding. Do this by selecting option 'Do not configure networking' from the list below.
    echo
    echo How would you like to proceed?:
    echo 1. Proceed with the above values
    echo 2. Change Network interface
    echo 3. Change IP address
    echo 4. Change Network mask
    echo 5. Change Network address
    echo 6. Change Host Gateway
    echo 7. Change DHCP range start
    echo 8. Change DHCP range end
    echo 9. Change DHCP Gateway
    echo 10. Change DNS forwarder
    echo 11. Change Domain
    echo 12. Change Foreman URL
    echo 13. Change NTP sync host
    echo 14. Do not configure networking
    echo 15. Do not configure firewall
    echo 16. Cancel Installation
}


print_vm_settings() {
    echo Configure client authentication
    echo           SSH public key: ''
    echo            Root Password: '********'
    echo
    echo Please set a default root password for newly provisioned machines.  If you choose not to set a password, it will be defaulted to 'spengler'.  The password must be a minimum of 8 characters.  You can also set a public ssh key which will be deployed to newly provisioned machines.
    echo
    echo 'How would you like to proceed?:.'
    echo '1. Proceed with the above values'
    echo '2. Change SSH public key'
    echo '3. Change Root Password'
}

print_rhel_repo() {
    echo 'Enter RHEL repo path:'
    echo '1. Set RHEL repo path (http or https URL): http://'
    echo '2. Proceed with configuration'
    echo '3. Skip this step (provisioning wont work)'
}

print_subscription_manager() {
    echo Enter your subscription manager credentials:
    echo 1. Subscription manager username:
    echo 2. Subscription manager password:
    echo 3. Comma separated repositories:        rhel-7-server-openstack-5.0-rpms
    echo "4. Subscription manager pool (optional):"
    echo 5. Proceed with configuration
    echo "6. Skip this step (provisioning wont subscribe your machines)"
}

print_success(){
    echo Starting to seed provisioning data
    echo Use 'base_RedHat_7' hostgroup for provisioning
    echo Success!
    echo   * Foreman is running at https://hp-bl660cgen8-01.rhts.eng.bos.redhat.com
    echo       Default credentials are 'admin:changeme'
    echo   * Foreman Proxy is running at https://hp-bl660cgen8-01.rhts.eng.bos.redhat.com:8443
    echo   * Puppetmaster is running at port 8140
    echo   The full log is at /var/log/foreman-installer/foreman-installer.log
    echo
}

print_select_nic() {
    echo 'Please select NIC on which you want Foreman provisioning enabled:'
    echo '1. eth3'
    echo '2. eth2'
    echo '3. eth1'
    echo '4. eth0'
    echo '5. virbr0'
    echo '6. virbr0_nic'
    echo '7. vnet3'
    echo '8. vnet2'
    echo '9. vnet1'
    echo '10. vnet0'
    echo '?'
}

print_post_config() {
    echo Installing             Done                                               [100%] [..........]
    echo Starting configuration...
    echo Warning: Sections other than main, master, agent, user are deprecated in puppet.conf. Please u
    echo "se the directory environments feature to specify environments. (See http://docs.puppetlabs.com"
    echo "/puppet/latest/reference/environments.html)"
    echo "  (at /usr/lib/ruby/site_ruby/1.8/puppet/settings/config_file.rb:77:in collect) "
    echo
    echo Now you should configure installation media which will be used for provisioning.
    echo Note that if you dont configure it properly, host provisioning wont work until you configure
    echo installation media manually.
    echo
}

# Enter RHEL repo path: 1. Set RHEL repo path (http or https URL): http://download.eng.bos.redhat.com/rel-eng/repos/rhel-7.0/x86_64/
main() {
    echo > answer.txt
    if random_true_false; then
        print_select_nic
        answer "NIC selection (virbr0)"
    else
        print_settings_change
        answer "select: NIC selection (2)"
        print_select_nic
        answer "NIC selection (virbr0)"
    fi


    print_settings_change
    answer "select: DHCP range start (7)"

    echo "new value for DHCP range start"
    answer 'DHCP Range start'

    print_settings_change
    answer 'select: ntp url (13)'
    echo "new value for ntp url"
    answer 'New ntp url'

    print_settings_change
    answer 'select: disable network (14)'

    print_settings_change
    answer 'select: disable firewall (15)'

    print_settings_change
    answer 'select: proceed (1)'

    print_vm_settings
    answer 'vm confimation (1)'
    print_post_config

    sleep 5
    print_rhel_repo
    answer 'rhel repo path (1)'
    echo 'Path: '
    answer 'rhel repo (url)'

    print_subscription_manager
    answer 'skip subscription (6)'
    print_success
}

main "$@"
