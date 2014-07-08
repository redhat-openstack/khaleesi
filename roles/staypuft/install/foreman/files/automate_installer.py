#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automates rhel-osp-installer command
"""

import pexpect
import sys


def set_value(child, key, value, menu_index, timeout, skip_input=False):
    value_set_already = key + ' .*' + value
    selection = child.expect([value_set_already, key], timeout)
    if selection == 0:
        return

    child.sendline(menu_index)
    if not skip_input:
        child.sendline(value)


def main(args):
    child = pexpect.spawn('rhel-osp-installer')
    child.logfile = sys.stdout

    nic_select = 'Please select NIC.*\r\n?.*'
    change_settings = 'How would you like to proceed.*\r\n.*'
    selection = child.expect([nic_select, change_settings], timeout=50)
    if selection == 1:
        child.sendline('2')
    child.sendline('virbr0')

    dhcp_start_range = 'DHCP range start:'
    dhcp_start_value = '192.168.100.200'
    set_value(child, dhcp_start_range, dhcp_start_value, '7', 5)

    ntp_server = 'NTP sync host:'
    ntp_value = 'clock.redhat.com'
    set_value(child, ntp_server, ntp_value, '13', 5)


    nw_config = 'Configure networking on this machine:'
    nw_value = '✗'
    set_value(child, nw_config, nw_value, '14', 5, skip_input=True)


    fw_config = 'Configure firewall on this machine:'
    fw_value = '✗'
    set_value(child, fw_config, fw_value, '15', 5, skip_input=True)

    child.expect(change_settings, timeout=5)
    child.sendline('1')

    client_auth = 'Configure client authentication.*\r\n'
    child.expect(client_auth, timeout=5)
    child.sendline('1')

    repo_path = 'Set RHEL repo path.*\r\n'
    child.expect(repo_path, timeout=300)
    child.sendline('1')
    child.sendline(
        'http://download.eng.bos.redhat.com/rel-eng/repos/rhel-7.0/x86_64/')
    child.sendline('2')

    subscription_cred = 'Enter your subscription manager.*\r\n'
    child.expect(subscription_cred, timeout=15)
    child.sendline('6')

    child.expect('Success!', timeout=300)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
