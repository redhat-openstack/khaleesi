#! /usr/bin/env python

import pexpect
import sys


def main(args):
    child = pexpect.spawn('rhel-osp-installer')
    child.logfile = sys.stdout

    nic_select = 'Please select NIC.*\r\n?.*'
    change_settings = 'How would you like to proceed.*\r\n.*'
    selection = child.expect([nic_select, change_settings], timeout=50)
    if selection == 1:
        child.sendline('2')
    child.sendline('virbr0')

    child.expect(change_settings, timeout=15)
    child.sendline('7')
    child.sendline('192.168.100.200')

    child.expect(change_settings, timeout=5)
    child.sendline('13')
    child.sendline('clock.redhat.com')

    child.expect(change_settings, timeout=5)
    child.sendline('14')

    child.expect(change_settings, timeout=5)
    child.sendline('15')

    child.expect(change_settings, timeout=5)
    child.sendline('1')

    client_auth = 'Configure client authentication.*\r\n'
    child.expect(client_auth, timeout=5)
    child.sendline('1')

    repo_path = 'Set RHEL repo path.*\r\n'
    child.expect(repo_path, timeout=180)
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
