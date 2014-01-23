#!/usr/bin/python
#coding: utf-8 -*-

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

try:
    from novaclient.v1_1 import client as nova_client
    try:
        from neutronclient.neutron import client
    except ImportError:
        from quantumclient.quantum import client
    from keystoneclient.v2_0 import client as ksclient
    import time
except ImportError:
    print "failed=True msg='novaclient, keystone, and quantumclient (or neutronclient) client are required'"

DOCUMENTATION = '''
---
module: quantum_floating_ip_allocate
version_added: "1.4"
short_description: Allocate or deallocate a floating IP for use with a tenant
description:
   - Allocate or deallocate a floating IP for use with a tenant
options:
   login_username:
     description:
        - login username to authenticate to keystone
     required: true
     default: admin
   login_password:
     description:
        - password of login user
     required: true
     default: 'yes'
   login_tenant_name:
     description:
        - the tenant name of the login user
     required: true
     default: true
   auth_url:
     description:
        - the keystone url for authentication
     required: false
     default: 'http://127.0.0.1:35357/v2.0/'
   region_name:
     description:
        - name of the region
     required: false
     default: None
   state:
     description:
        - indicates the desired state of the resource
     choices: ['present', 'absent']
     default: present
   network_name:
     description:
        - Name of the network from which IP has to be assigned to VM. Please make sure the network is an external network
     required: false
     default: None
   ip_address:
     description:
        - floating ip that should be assigned to the tenant
     required: false
     default: None
requirements: ["quantumclient", "neutronclient", "keystoneclient"]
'''

EXAMPLES = '''
# Allocate a floating IP for use in a tenant
- quantum_floating_ip_allocate:
           state=present
           login_username=admin
           login_password=admin
           login_tenant_name=admin
           network_name=external

# Deallocate (release) a floating IP from a tenant
- quantum_floating_ip_allocate:
           state=absent
           login_username=admin
           login_password=admin
           login_tenant_name=admin
           ip_address=1.1.1.1
'''

def _get_ksclient(module, kwargs):
    try:
        kclient = ksclient.Client(username=kwargs.get('login_username'),
                                 password=kwargs.get('login_password'),
                                 tenant_name=kwargs.get('login_tenant_name'),
                                 auth_url=kwargs.get('auth_url'))
    except Exception as e:
        module.fail_json(msg = "Error authenticating to the keystone: %s " % e.message)
    global _os_keystone
    _os_keystone = kclient
    return kclient


def _get_endpoint(module, ksclient):
    try:
        endpoint = ksclient.service_catalog.url_for(service_type='network', endpoint_type='publicURL')
    except Exception as e:
        module.fail_json(msg = "Error getting network endpoint: %s" % e.message)
    return endpoint

def _get_neutron_client(module, kwargs):
    _ksclient = _get_ksclient(module, kwargs)
    token = _ksclient.auth_token
    endpoint = _get_endpoint(module, _ksclient)
    kwargs = {
            'token': token,
            'endpoint_url': endpoint
    }
    try:
        neutron = client.Client('2.0', **kwargs)
    except Exception as e:
        module.fail_json(msg = "Error in connecting to neutron: %s " % e.message)
    return neutron

def _get_floating_ip_id(module, neutron):
    kwargs = {
        'floating_ip_address': module.params['ip_address']
    }
    try:
        ips = neutron.list_floatingips(**kwargs)
    except Exception as e:
        module.fail_json(msg = "error in fetching the floatingips's %s" % e.message)
    if not ips['floatingips']:
        module.exit_json(changed = False)
    ip = ips['floatingips'][0]['id']
    if not ips['floatingips'][0]['port_id']:
        state = "detached"
    else:
        state = "attached"
    return state, ip

def _get_network_id(neutron, module):
    try:
        for network in neutron.list_networks():
            if network:
                if network['name'] == module.params['network_name']:
                    if network['status'] != 'ACTIVE' and module.params['state'] == 'present':
                        module.fail_json( msg="The network is available but not Active. state:" + network['status'])
                    network_id = network['id']
                    break
    except Exception as e:
        module.fail_json(msg = "error in fetching the floating ip network %s" % e.message)
    return network_id, network

def _create_floating_ip(neutron, module, network_id):
    kwargs = {
        'floating_network_id': network_id
    }
    try:
        result = neutron.create_floatingip({'floatingip': kwargs})
    except Exception as e:
        module.fail_json(msg = "error in create floating ip %s" % e.message)
    module.exit_json(changed = True, result = result, floating_ip=result['floatingip']['floating_ip_address'])

def _delete_floating_ip(neutron, module, floating_ip_id):
    try:
        result = neutron.delete_floatingip(floating_ip_id)
    except Exception as e:
        module.fail_json(msg = "There was an error in deleting the floating ip address: %s" % e.message)
    module.exit_json(changed = True, result = result, floating_ip=module.params['ip_address'])

def main():

    module = AnsibleModule(
        argument_spec                   = dict(
            login_username                  = dict(default='admin'),
            login_password                  = dict(required=True),
            login_tenant_name               = dict(required='True'),
            auth_url                        = dict(default='http://127.0.0.1:35357/v2.0/'),
            region_name                     = dict(default=None),
            network_name                    = dict(required=False),
            ip_address                      = dict(required=False),
            state                           = dict(default='present', choices=['absent', 'present'])
        ),
    )

    try:
        nova = nova_client.Client(module.params['login_username'], module.params['login_password'],
                                 module.params['login_tenant_name'], module.params['auth_url'], service_type='compute')
    except Exception as e:
        module.fail_json( msg = " Error in authenticating to nova: %s" % e.message)
    neutron = _get_neutron_client(module, module.params)
    if module.params['state'] == 'present':
        network_id, network = _get_network_id(neutron, module)
        _create_floating_ip(neutron, module, network_id)

    if module.params['state'] == 'absent':
        state, floating_ip_id = _get_floating_ip_id(module, neutron)
        _delete_floating_ip(neutron, module, floating_ip_id)

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
main()

