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
module: nova_floating_ip
version_added: ".1"
short_description: Create and assign a floating ip
description:
   - Create and assign a floating ip
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
requirements: ["novaclient"]
'''

EXAMPLES = '''
# Creates a new floating ip address and assigns it to the instance if one is not already assigned.
- nova_floating_ip:
       state: present
       login_username: admin
       login_password: admin
       login_tenant_name: admin
       network_name: public
       instance_name: vm1
'''

def _create_floating_ip(module, nova):
    try:
        result = nova.floating_ips.create(module.params['network_name'])
    except Exception, e:
        module.fail_json(msg="There was an error in updating the floating ip address: %s" % e.message)
    return result

def _assign_floating_ip(module, nova, floating_ip):
    name = None
    server_list = None
    server_list = nova.servers.list(True, {'name': module.params['instance_name']})
    if server_list:
        instance = nova.servers.find(name=module.params['instance_name'])
        try:
            result = instance.add_floating_ip(floating_ip)
        except Exception, e:
            module.fail_json(msg="There was an error in updating the floating ip address: %s" % e.message)
        #must resturn the floating_ip object that was assigned, not the result
        return floating_ip
    else:
        module.fail_json(msg="No instances were found")

def _remove_floating_ip(module, nova, floating_ip):
    name = None
    server_list = None
    server_list = nova.servers.list(True, {'name': module.params['instance_name']})
    if server_list:
        instance = nova.servers.find(name=module.params['instance_name'])
        floating_ip_object = [x for x in nova.floating_ips.list() if x.ip == floating_ip]
        try:
            result = nova.floating_ips.delete(floating_ip_object[0])
        except Exception, e:
            #unassociate the float that could not be deleted
            instance.remove_floating_ip(floating_ip);
            module.fail_json(msg="There was an error  removing ip address: %s %s" % (floating_ip, e.message))
    else:
        module.fail_json(msg="No instances were found")


def _get_server_floating_ip(module, nova):
    server = None
    floating_ips = []
    try:
        servers = nova.servers.list(True, {'name': module.params['instance_name']})
        if servers:
            server = [x for x in servers if x.name == module.params['instance_name']][0]
    except Exception, e:
        module.fail_json(msg = "Error in getting the server list: %s" % e.message)
    if server :
        if module.params['state'] == 'present' and  server.status != 'ACTIVE':
            module.fail_json( msg="VM exists but not Active. state: " + server.status)
        for net in getattr(server, 'addresses').itervalues():
          for x in net:
            if 'OS-EXT-IPS:type' in x and x['OS-EXT-IPS:type'] == 'floating':
              return x['addr']
    else:
        module.fail_json(msg="No instances were found")

def _associate_floating_ip(module, nova):
    floating_ip = _get_server_floating_ip(module, nova)
    if floating_ip:
        return floating_ip
    # create one if there isn't
    floating_ip = _create_floating_ip(module, nova)
    if floating_ip:
        _assign_floating_ip(module, nova, floating_ip)
        return floating_ip
    else:
        module.fail_json(msg="Failed to assign floating ip", changed=False)


def _release_floating_ip(module, nova):
    floating_ip = _get_server_floating_ip(module, nova)
    if floating_ip:
        _remove_floating_ip(module, nova, floating_ip)
        module.exit_json(changed=True, result="Removed")
    else:
        module.fail_json(msg = "Unable to fetch floating ip")


def main():
    module = AnsibleModule(
        argument_spec       = dict(
        login_username      = dict(default='admin'),
        login_password      = dict(required=True),
        login_tenant_name   = dict(required='True'),
        auth_url            = dict(default='http://127.0.0.1:35357/v2.0/'),
        network_name        = dict(required=True),
        instance_name       = dict(required=True),
        state               = dict(default='present', choices=['absent', 'present'])
        ),
    )

    nova = nova_client.Client(
        module.params['login_username'],
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

    if module.params['state'] == 'present':
        floating_ip = _associate_floating_ip(module, nova)
        if hasattr(floating_ip, 'ip'):
            floating_ip = floating_ip.ip
        module.exit_json(changed=True, result=floating_ip, public_ip=floating_ip)

    elif module.params['state'] == 'absent':
        _release_floating_ip(module, nova)
        module.exit_json(changed=True)

from ansible.module_utils.basic import *
main()