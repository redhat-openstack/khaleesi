#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2014, Wes Hayutin <weshayutin@gmail.com> 
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
    import time
except ImportError:
    print("failed=True msg='novaclient is required for this module'")

DOCUMENTATION = '''
---
module: nova_snapshot
version_added: ".1"
short_description: Create a snapshot of a running instance
description:
   - Create a snapshot of a running instance
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
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     default: present
   instance_name:
     description:
        - Name that has to be given to the instance
     required: true
     default: None
   snapshot_name
     description:
       - Name given to the snapshot to be created
     required: true
     default: None
   wait_snapshot:
     description:
        - If the module should wait for the image to be created.
     required: false
     default: 'yes'
   wait_for:
     description:
        - The amount of time the module should wait for the image to get into active state
     required: false
     default: 1200
requirements: ["novaclient"]
'''

EXAMPLES = '''
# Creates a new new snapshot of the instance
- nova_snapshot:
       state: present
       login_username: admin
       login_password: admin
       login_tenant_name: admin
       instance_name: vm1
       snapshot_name: vm1_snapshot1
       wait_snapshot: yes
       wait_for: 7200
'''

def _create_snapshot(module, nova, server):
    try:
        snapshot_id = nova.servers.create_image(server, module.params['snapshot_name'])
    except Exception, e:
        module.fail_json(msg="There was an error snapshoting the instance: %s" % e.message)
    wait = module.params['wait_snapshot']
    if  wait == 'yes' or wait == 'True'  or wait == True:
        expire = time.time() + int(module.params['wait_for'])
        while time.time() < expire:
            try:
                image = nova.images.get(snapshot_id)
            except Exception, e:
                module.fail_json( msg = "Error in getting info from image: %s " % e.message)
            if image.status == 'ACTIVE':
                module.exit_json(changed = True, result=image.id,  status = image.status, info = image._info)
            if image.status == 'ERROR':
                module.fail_json(msg = "Error in creating the server, please check logs")
            time.sleep(60)
        module.fail_json(msg = "Timeout waiting for the image to become active.. Please check manually")
    else:
        try:
            image = nova.images.get(snapshot_id)
        except Exception, e:
            module.fail_json( msg = "Error in getting info from image: %s " % e.message)
    if image.status == 'ERROR':
        module.fail_json(msg = "Error in creating the image.. Please check manually")
    module.exit_json(changed = True, result = image.id,  status = image.status, info = image._info)

def _get_server(module, nova):
    server = None
    try:
        servers = nova.servers.list(False)
        if servers:
            server = nova.servers.find(name=module.params['instance_name'])
    except Exception, e:
        module.fail_json(msg = "Error in getting the server list: %s" % e.message)
    if server and module.params['state'] == 'present':
        if server.status != 'ACTIVE':
            module.fail_json( msg="The VM is available but not Active. state:" + server.status)
    return server

def main():
    module = AnsibleModule(
        argument_spec                   = dict(
        login_username                  = dict(default='admin'),
        login_password                  = dict(required=True),
        login_tenant_name               = dict(required='True'),
        auth_url                        = dict(default='http://127.0.0.1:35357/v2.0/'),
        instance_name                   = dict(required=True),
        snapshot_name                   = dict(required=True),
        state                           = dict(default='present', choices=['absent', 'present']),
        wait_snapshot                         = dict(default='yes'),
        wait_for                    =  dict(default='7200')
        ),
    )

    nova = nova_client.Client(module.params['login_username'],
                              module.params['login_password'],
                              module.params['login_tenant_name'],
                              module.params['auth_url'],
                              service_type='compute')
    try:
        nova.authenticate()
    except exc.Unauthorized, e:
        module.fail_json(msg = "Invalid OpenStack Nova credentials.: %s" % e.message)
    except exc.AuthorizationFailure, e:
        module.fail_json(msg = "Unable to authorize user: %s" % e.message)

    server = _get_server(module, nova)
    if server:
        _create_snapshot(module, nova, server)
    else:
        module.exit_json(changed=False)

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
main()

