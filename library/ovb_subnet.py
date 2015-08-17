#!/usr/bin/python
#coding: utf-8 -*-

try:
    from neutronclient.neutron import client
    from neutronclient.common import exceptions
    from keystoneclient.v2_0 import client as ksclient
    from netaddr import IPNetwork
except ImportError:
    print("failed=True msg='neutronclient, keystoneclient are required'")

DOCUMENTATION = '''
---
module: ovb_subnet
   - Add/remove subnet from a network
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
     default: True
   login_tenant_name:
     description:
        - The tenant name of the login user
     required: true
     default: True
   auth_url:
     description:
        - The keystone URL for authentication
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
   network_name:
     description:
        - Name of the network to which the subnet should be attached
     required: true
     default: None
   name:
     description:
       - The name of the subnet that should be created
     required: true
     default: None
   cidr:
     description:
        - The CIDR representation of the subnet that should be assigned to the subnet
     required: false
     default: 10.0.0.0/24
   tenant_name:
     description:
        - The name of the tenant for whom the subnet should be created
     required: false
     default: None
   ip_version:
     description:
        - The IP version of the subnet 4
     required: false
     default: 4
   enable_dhcp:
     description:
        - Whether DHCP should be enabled for this subnet.
     required: false
     default: true
   gateway_ip:
     description:
        - The ip that would be assigned to the gateway for this subnet
     required: false
     default: 10.0.0.1
   dns_nameservers:
     description:
        - DNS nameservers for this subnet, comma-separated
     required: false
     default: None
     version_added: "1.4"
   allocation_pool_start:
     description:
        - From the subnet pool the starting address from which the IP should be allocated
     required: false
     default: 10.0.0.10
   allocation_pool_end:
     description:
        - From the subnet pool the last IP that should be assigned to the virtual machines
     required: 10.0.0.40
     default: None
requirements: ["neutronclient", "keystoneclient"]
'''

EXAMPLES = '''
# Create a subnet for a tenant with the specified subnet
'''

_os_keystone   = None
_os_tenant_id  = None
_os_network_id = None
_inc = 0

def _get_ksclient(module, kwargs):
    try:
        kclient = ksclient.Client(username=kwargs.get('login_username'),
                                 password=kwargs.get('login_password'),
                                 tenant_name=kwargs.get('login_tenant_name'),
                                 auth_url=kwargs.get('auth_url'))
    except Exception, e:
        module.fail_json(msg = "Error authenticating to the keystone: %s" %e.message)
    global _os_keystone
    _os_keystone = kclient
    return kclient


def _get_endpoint(module, ksclient):
    try:
        endpoint = ksclient.service_catalog.url_for(service_type='network', endpoint_type='publicURL')
    except Exception, e:
        module.fail_json(msg = "Error getting network endpoint: %s" % e.message)
    return endpoint

def _get_neutron_client(module, kwargs):
    _ksclient = _get_ksclient(module, kwargs)
    token     = _ksclient.auth_token
    endpoint  = _get_endpoint(module, _ksclient)
    kwargs = {
            'token':        token,
            'endpoint_url': endpoint
    }
    try:
        neutron = client.Client('2.0', **kwargs)
    except Exception, e:
        module.fail_json(msg = " Error in connecting to neutron: %s" % e.message)
    return neutron

def _set_tenant_id(module):
    global _os_tenant_id
    if not module.params['tenant_name']:
        tenant_name = module.params['login_tenant_name']
    else:
        tenant_name = module.params['tenant_name']

    for tenant in _os_keystone.tenants.list():
        if tenant.name == tenant_name:
            _os_tenant_id = tenant.id
            break
    if not _os_tenant_id:
            module.fail_json(msg = "The tenant id cannot be found, please check the parameters")

def _get_net_id(neutron, module):
    kwargs = {
        'tenant_id': _os_tenant_id,
        'name': module.params['network_name'],
    }
    try:
        networks = neutron.list_networks(**kwargs)
    except Exception, e:
        module.fail_json("Error in listing neutron networks: %s" % e.message)
    if not networks['networks']:
            return None
    return networks['networks'][0]['id']


def _get_subnet_id(module, neutron):
    global _os_network_id
    subnet_id = None
    _os_network_id = _get_net_id(neutron, module)
    if not _os_network_id:
        module.fail_json(msg = "network id of network not found.")
    else:
        kwargs = {
            'tenant_id': _os_tenant_id,
            'name': module.params['name'],
        }
        try:
            subnets = neutron.list_subnets(**kwargs)
        except Exception, e:
            module.fail_json( msg = " Error in getting the subnet list:%s " % e.message)
        if not subnets['subnets']:
            return None
        return subnets['subnets'][0]['id']

def _create_subnet(module, neutron):
    neutron.format = 'json'
    cidr = _get_available_cidr(module, neutron, module.params['cidr'])
    subnet = {
            'name':            module.params['name'],
            'ip_version':      module.params['ip_version'],
            'enable_dhcp':     module.params['enable_dhcp'],
            'tenant_id':       _os_tenant_id,
            'gateway_ip':      str(IPNetwork(cidr)[module.params['gateway_ip'].split('.')[3]]),
            'dns_nameservers': module.params['dns_nameservers'],
            'network_id':      _os_network_id,
            'cidr':            cidr,
    }
    if module.params['allocation_pool_start'] and module.params['allocation_pool_end']:
        allocation_pools = [
            {
                'start' : str(IPNetwork(cidr)[module.params['allocation_pool_start'].split('.')[3]]),
                'end'   :  str(IPNetwork(cidr)[module.params['allocation_pool_end'].split('.')[3]]) 
            }
        ]
        subnet.update({'allocation_pools': allocation_pools})
    if not module.params['gateway_ip']:
        subnet.pop('gateway_ip')
    if module.params['dns_nameservers']:
        subnet['dns_nameservers'] = module.params['dns_nameservers'].split(',')
    else:
        subnet.pop('dns_nameservers')
    try:
        new_subnet = neutron.create_subnet(dict(subnet=subnet))
    except Exception, e:
        module.fail_json(msg = "Failure in creating subnet: %s" % e.message)
    return new_subnet['subnet']['id']


def _delete_subnet(module, neutron, subnet_id):
    try:
        neutron.delete_subnet(subnet_id)
    except Exception, e:
        module.fail_json( msg = "Error in deleting subnet: %s" % e.message)
    return True

def _list_existing_cidr(module, neutron):
    subnets = neutron.list_subnets()['subnets']
    return [subnet['cidr']  for subnet in subnets]

def _get_available_cidr(module, neutron, cidr):
    current_cidrs = _list_existing_cidr(module, neutron)
    global _inc
    if _inc == 10:
        raise Exception("Not enough cidr available on your deployment")
    if cidr in current_cidrs:
        _inc += 1
        next_cidr =  IPNetwork(cidr).next()
        return _get_available_cidr(module, neutron, str(next_cidr))
    return str(cidr)

def main():

    argument_spec = openstack_argument_spec()
    argument_spec.update(dict(
            name                    = dict(required=True),
            network_name            = dict(required=True),
            cidr                    = dict(default='10.0.0.0/24'),
            tenant_name             = dict(default=None),
            state                   = dict(default='present', choices=['absent', 'present']),
            ip_version              = dict(default='4', choices=['4']),
            enable_dhcp             = dict(default='true', type='bool'),
            gateway_ip              = dict(default='10.0.0.1'),
            dns_nameservers         = dict(default=None),
            allocation_pool_start   = dict(default='10.0.0.10'),
            allocation_pool_end     = dict(default='10.0.0.40'),
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    neutron = _get_neutron_client(module, module.params)
    _set_tenant_id(module)
    if module.params['state'] == 'present':
        subnet_id = _get_subnet_id(module, neutron)
        if not subnet_id:
            subnet_id = _create_subnet(module, neutron)
            module.exit_json(changed = True, result = "Created" , id = subnet_id)
        else:
            module.exit_json(changed = False, result = "success" , id = subnet_id)
    else:
        subnet_id = _get_subnet_id(module, neutron)
        if not subnet_id:
            module.exit_json(changed = False, result = "success")
        else:
            _delete_subnet(module, neutron, subnet_id)
            module.exit_json(changed = True, result = "deleted")

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
main()
