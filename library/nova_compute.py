#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2013, Benno Joy <benno@ansible.com>
# (c) 2013, John Dewey <john@dewey.ws>
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
    from novaclient import exceptions
except ImportError:
    print("failed=True msg='novaclient is required for this module'")

import pprint
import time

DOCUMENTATION = '''
---
module: nova_compute
version_added: "1.2"
short_description: Create/Delete VMs from OpenStack
description:
   - Create or Remove virtual machines from Openstack.
options:
   login_username:
     description:
        - login username to authenticate to keystone
     required: true
     default: admin
   login_password:
     description:
        - Password of login user
     required: true
     default: 'yes'
   login_tenant_name:
     description:
        - The tenant name of the login user
     required: true
     default: 'yes'
   auth_url:
     description:
        - The keystone url for authentication
     required: false
     default: 'http://127.0.0.1:35357/v2.0/'
   region_name:
     description:
        - Name of the region
     required: false
     default: None
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     default: present
   name:
     description:
        - Name that has to be given to the instance
     required: true
     default: None
   image_id:
     description:
        - The id of the image that has to be cloned
     required: true
     default: None
   flavor_id:
     description:
        - The id of the flavor in which the new VM has to be created
     required: false
     default: 1
   key_name:
     description:
        - The key pair name to be used when creating a VM
     required: false
     default: None
   security_groups:
     description:
        - The name of the security group to which the VM should be added
     required: false
     default: None
   nics:
     description:
        - A list of network id's to which the VM's interface should be attached
     required: false
     default: None
   meta:
     description:
        - A list of key value pairs that should be provided as a metadata to the new VM
     required: false
     default: None
   wait:
     description:
        - If the module should wait for the VM to be created.
     required: false
     default: 'yes'
   wait_for:
     description:
        - The amount of time the module should wait for the VM to get into active state
     required: false
     default: 180
   user_data:
     description:
        - Opaque blob of data which is made available to the instance
     required: false
     default: None
     version_added: "1.6"
   config_drive:
     description:
        - Enable a config drive to be attached to the instance
     required: false
     default: false
     version_added: "1.6"
requirements: ["novaclient"]
'''

EXAMPLES = '''
# Creates a new VM and attaches to a network and passes metadata to the instance
- nova_compute:
       state: present
       login_username: admin
       login_password: admin
       login_tenant_name: admin
       name: vm1
       image_id: 4f905f38-e52a-43d2-b6ec-754a13ffb529
       key_name: ansible_key
       wait_for: 200
       flavor_id: 4
       nics:
         - net-id: 34605f38-e52a-25d2-b6ec-754a13ffb723
       meta:
         hostname: test1
         group: uge_master
'''

def _delete_server(module, nova):
    name = None
    server_list = None
    try:
        server_list = nova.servers.list(True, {'name': module.params['name']})
        if server_list:
            server = [x for x in server_list if x.name == module.params['name']]
            nova.servers.delete(server.pop())
    except Exception, e:
        module.fail_json( msg = "Error in deleting vm: %s" % e.message)
    if module.params['wait'] == 'no':
        module.exit_json(changed = True, result = "deleted")
    expire = time.time() + int(module.params['wait_for'])
    while time.time() < expire:
        name = nova.servers.list(True, {'name': module.params['name']})
        if not name:
            module.exit_json(changed = True, result = "deleted")
        time.sleep(5)
    module.fail_json(msg = "Timed out waiting for server to get deleted, please check manually")


def _create_server(module, nova):
    bootargs = [module.params['name'], module.params['image_id'], module.params['flavor_id']]
    bootkwargs = {
                'nics' : module.params['nics'],
                'meta' : module.params['meta'],
                'key_name': module.params['key_name'],
                'security_groups': module.params['security_groups'].split(','),
                #userdata is unhyphenated in novaclient, but hyphenated here for consistency with the ec2 module:
                'userdata': module.params['user_data'],
                'config_drive': module.params['config_drive'],
    }
    if not module.params['key_name']:
        del bootkwargs['key_name']

    def nova_create():
        try:
            server = nova.servers.create(*bootargs, **bootkwargs)
            server = nova.servers.get(server.id)
            return server
        except Exception, e:
            module.fail_json(msg = "Error in creating instance: %s " % e.message)

    server = nova_create()
    wait = module.params['wait'] == 'yes'
    expire = time.time() + int(module.params['wait_for'])
    while True:
        try:
            server = nova.servers.get(server.id)
        except Exception, e:
            module.fail_json(msg = "Error in getting instance  %s: %s " % (server.id, e.message))
        if server.status == 'ACTIVE':
            private = [ x['addr'] for x in getattr(server, 'addresses').itervalues().next() if 'OS-EXT-IPS:type' in x and x['OS-EXT-IPS:type'] == 'fixed']
            public  = [ x['addr'] for x in getattr(server, 'addresses').itervalues().next() if 'OS-EXT-IPS:type' in x and x['OS-EXT-IPS:type'] == 'floating']
            module.exit_json(changed = True, id = server.id, private_ip=''.join(private), public_ip=''.join(public), status = server.status, info = server._info)
        if server.status == 'ERROR':
            ENGOPS_328484_MSG = (
                'Timeout while waiting on RPC response - topic: "network"'
            )
            if ENGOPS_328484_MSG in server.fault.get('message', ''):
                # TODO(jhenner) Add warning or something like that.
                server.delete()
                server = nova_create()
                continue
            else:
                module.fail_json(msg=(
                    "Error in creating the server:\n%s"
                    % pprint.pformat(server._info)),
                    info = server._info
                )
        if not wait or time.time() >= expire:
            module.fail_json(msg = "Timeout waiting for the server to come up:\n%s" % server)
        time.sleep(2)


def _get_server_state(module, nova):
    server = None
    try:
        servers = nova.servers.list(True, {'name': module.params['name']})
        if servers:
            # the {'name': module.params['name']} will also return servers
            # with names that partially match the server name, so we have to
            # strictly filter here
            servers = [x for x in servers if x.name == module.params['name']]
            if servers:
                server = servers[0]
    except Exception, e:
        module.fail_json(msg = "Error in getting the server list: %s" % e.message)
    if server and module.params['state'] == 'present':
        if server.status != 'ACTIVE':
            module.fail_json( msg="The VM is available but not Active. state:" + server.status)
        private = [ x['addr'] for x in getattr(server, 'addresses').itervalues().next() if 'OS-EXT-IPS:type' in x and x['OS-EXT-IPS:type'] == 'fixed']
        public  = [ x['addr'] for x in getattr(server, 'addresses').itervalues().next() if 'OS-EXT-IPS:type' in x and x['OS-EXT-IPS:type'] == 'floating']
        module.exit_json(changed = False, id = server.id, public_ip = ''.join(public), private_ip = ''.join(private), info = server._info)
    if server and module.params['state'] == 'absent':
        return True
    if module.params['state'] == 'absent':
        module.exit_json(changed = False, result = "not present")
    return True



def main():
    module = AnsibleModule(
        argument_spec                   = dict(
        login_username                  = dict(default='admin'),
        login_password                  = dict(required=True),
        login_tenant_name               = dict(required='True'),
        auth_url                        = dict(default='http://127.0.0.1:35357/v2.0/'),
        region_name                     = dict(default=None),
        name                            = dict(required=True),
        image_id                        = dict(default=None),
        flavor_id                       = dict(default=1),
        key_name                        = dict(default=None),
        security_groups                 = dict(default='default'),
        nics                            = dict(default=None),
        meta                            = dict(default=None),
        wait                            = dict(default='yes', choices=['yes', 'no']),
        wait_for                        = dict(default=180),
        state                           = dict(default='present', choices=['absent', 'present']),
        user_data                       = dict(default=None),
        config_drive                    = dict(default=False)
        ),
    )

    nova = nova_client.Client(module.params['login_username'],
                              module.params['login_password'],
                              module.params['login_tenant_name'],
                              module.params['auth_url'],
                              region_name=module.params['region_name'],
                              service_type='compute')
    try:
        nova.authenticate()
    except exceptions.Unauthorized, e:
        module.fail_json(msg = "Invalid OpenStack Nova credentials.: %s" % e.message)
    except exceptions.AuthorizationFailure, e:
        module.fail_json(msg = "Unable to authorize user: %s" % e.message)

    if module.params['state'] == 'present':
        if not module.params['image_id']:
            module.fail_json( msg = "Parameter 'image_id' is required if state == 'present'")
        else:
            _get_server_state(module, nova)
            _create_server(module, nova)
    if module.params['state'] == 'absent':
        _get_server_state(module, nova)
        _delete_server(module, nova)

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
main()

