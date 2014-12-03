#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2014, Brad P. Crochet <brad@redhat.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
DOCUMENTATION = '''
---
module: custom_facts
version_added: "1.6"
short_description: Add a set of custom facts based on specific vars
description:
   - Add a set of custom facts based on specific vars
'''

EXAMPLES = '''
# Allocate a floating IP for use in a tenant
- custom_facts:
'''
import os
import syslog
syslog.openlog('ansible-%s' % os.path.basename(__file__))

# FIXME: this all should be moved to module_common, as it's
#        pretty much a copy from the callbacks/util code
DEBUG_LEVEL = 4


def log(msg, cap=0):
    if DEBUG_LEVEL >= cap:
        syslog.syslog(syslog.LOG_NOTICE | syslog.LOG_DAEMON, msg)


def v(msg):
    log(msg, cap=1)


def vv(msg):
    log(msg, cap=2)


def vvv(msg):
    log(msg, cap=3)


def vvvv(msg):
    log(msg, cap=4)


def _set_net_facts(facts, addresses):
    for address in addresses:
        facts[address] = addresses[address][0]['addr']


def _copy_node_data(node_data, key, facts, facts_key=None):
    facts_key = facts_key or key
    try:
        facts[facts_key] = node_data[key]
    except KeyError:
        pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            nodes_created_dict=dict(type='dict', required=True),
            floating_ip_dict=dict(type='dict', required=True),
        ),
    )

    nodes = module.params.get('nodes_created_dict')
    floating_ip = module.params.get('floating_ip_dict')

    facts = {}

    #  openstack node if info in the node
    if 'info' in nodes:
        facts['public_ip'] = floating_ip['public_ip']
        facts['private_ip'] = nodes['private_ip']
        net_ifaces = floating_ip['item']['value']['net_interfaces']
        facts['net_interfaces'] = net_ifaces
        addresses = nodes['info']['addresses']
        _set_net_facts(facts, addresses)

    elif 'instances' in nodes:
        rax_node = nodes['instances'][0]
        addresses = rax_node['rax_addresses']
        _set_net_facts(facts, addresses)
        facts['public_ip'] = rax_node['accessIPv4']
        facts['private_ip'] = rax_node['rax_addresses']['default'][0]['addr']
        facts['net_interfaces'] = rax_node['rax_addresses']

    node_data = nodes['item']['value']
    _copy_node_data(node_data, 'node_hostgroup', facts)
    _copy_node_data(node_data, 'bridge_interfaces', facts)
    _copy_node_data(node_data, 'hostname', facts, 'fqdn')
    _copy_node_data(node_data, 'hostname', facts, 'priv_hostname')

    result = {
        'ansible_facts': facts,
        'changed': True
    }
    module.exit_json(**result)

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
main()
