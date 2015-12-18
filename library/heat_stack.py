#!/usr/bin/python
#coding: utf-8 -*-

try:
    from time import sleep
    from keystoneclient.v2_0 import client as ksclient
    from heatclient.client import Client
    from heatclient.common import template_utils
    from heatclient.common import utils
except ImportError:
    print("failed=True msg='heatclient, keystoneclient are required'")

DOCUMENTATION = '''
---
module: heat_stack
   - Add/list and delete heat stack
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
   stack_name:
     description:
        - Name of the stack that should be created
     required: true
     default: None
   template:
     description:
       - Path of the template file to use for the stack creation
     required: false
     default: None
   environment:
     description:
        - List of environment files that should be used for the stack creation
     required: false
     default: None
requirements: ["heatclient", "keystoneclient"]
'''

EXAMPLES = '''
# Create a stack with given template and environment files
- name: create stack
  heat_stack:
    stack_name: test
    state: present
    login_username: admin
    login_password: admin
    auth_url: http://192.168.1.14:5000/v2.0
    login_tenant_name: admin
    tenant_name: admin
    template: /home/stack/test.yaml
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
        endpoint = ksclient.service_catalog.url_for(service_type='orchestration', endpoint_type='publicURL')
    except Exception, e:
        module.fail_json(msg = "Error getting network endpoint: %s" % e.message)
    return endpoint

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

def _get_heat_client(module, kwargs):
    _ksclient = _get_ksclient(module, kwargs)
    token     = _ksclient.auth_token
    endpoint  = _get_endpoint(module, _ksclient)
    try:
        heat = Client('1', endpoint=endpoint, token=token)
    except Exception, e:
        module.fail_json(msg = " Error in connecting to heat: %s" % e.message)
    return heat

def _create_stack(module, heat):
    heat.format = 'json'
    template_file = module.params['template']
    env_file = module.params['environment_files']
    tpl_files, template = template_utils.get_template_contents(template_file)
    env_files, env = template_utils.process_multiple_environments_and_files(env_paths=env_file)

    stack = heat.stacks.create(stack_name=module.params['stack_name'],
                               template=template,
                               environment=env,
                               files=dict(list(tpl_files.items()) + list(env_files.items())),
                               parameters={})
    uid = stack['stack']['id']

    stack = heat.stacks.get(stack_id=uid).to_dict()
    while stack['stack_status'] == 'CREATE_IN_PROGRESS':
        stack = heat.stacks.get(stack_id=uid).to_dict()
        sleep(5)
    if stack['stack_status'] == 'CREATE_COMPLETE':
        return stack['stack']['id']
    else:
        module.fail_json(msg = "Failure in creating stack: ".format(stack))

def _list_stack(module, heat):
    fields = ['id', 'stack_name', 'stack_status', 'creation_time',
              'updated_time']
    uids = []
    stacks = heat.stacks.list()
    return utils.print_list(stacks, fields)

def _delete_stack(module, heat):
    heat.stacks.delete(module.param['stack_name'])
    return _list_stack

def _get_stack_id(module, heat):
    stacks = heat.stacks.list()
    while True:
        try:
            stack = stacks.next()
            if module.param['stack_name'] == stack.stack_name:
                return stack.id
        except StopIteration:
            break
            return False

def main():

    argument_spec = openstack_argument_spec()
    argument_spec.update(dict(
            stack_name              = dict(required=True),
            template                = dict(default=None),
            environment_files       = dict(default=None, type='dict'),
            state                   = dict(default='present', choices=['absent', 'present']),
            tenant_name             = dict(default=None),
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    heat = _get_heat_client(module, module.params)
    _set_tenant_id(module)
    if module.params['state'] == 'present':
        stack_id = _get_stack_id(module, heat)
        if not stack_id:
            stack_id = _create_stack(module, heat)
            module.exit_json(changed = True, result = "Created" , id = stack_id)
        else:
            module.exit_json(changed = False, result = "success" , id = stack_id)
    else:
        stack_id = _get_stack_id(module, stack)
        if not stack_id:
            module.exit_json(changed = False, result = "success")
        else:
            _delete_stack(module, stack, stack_id)
            module.exit_json(changed = True, result = "deleted")

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
main()
