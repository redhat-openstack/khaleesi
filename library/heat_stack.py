#!/usr/bin/python
#coding: utf-8 -*-

try:
    import time
    from keystoneclient.v2_0 import client as ksclient
    from heatclient.client import Client
    from heatclient.common import template_utils
    from heatclient.common import utils
except ImportError:
    print("failed=True msg='heatclient and keystoneclient is required'")

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
   environment_files:
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
    login_username: admin
    login_password: admin
    auth_url: "http://192.168.1.14:5000/v2.0"
    tenant_name: admin
    stack_name: test
    state: present
    template: "/home/stack/ovb/templates/quintupleo.yaml"
    environment_files: ['/home/stack/ovb/templates/resource-registry.yaml','/home/stack/ovb/templates/env.yaml']

    - name: delete stack
      heat_stack:
        stack_name: test
        state: absent
        login_username: admin
        login_password: admin
        auth_url: "http://192.168.1.14:5000/v2.0"
        tenant_name: admin
'''

def obj_gen_to_dict(gen):
    """Enumerate through generator of object and return lists of dictonaries.
    """
    obj_list = []
    for obj in gen:
        obj_list.append(obj.to_dict())
    return obj_list


class Stack(object):

    def __init__(self, kwargs):
        self.client = self._get_client(kwargs)

    def _get_client(self, kwargs, endpoint_type='publicURL'):
        """ get heat client """
        kclient = ksclient.Client(**kwargs)
        token = kclient.auth_token
        endpoint = kclient.service_catalog.url_for(service_type='orchestration',
                                                    endpoint_type=endpoint_type)
        kwargs = {
                'token': token,
        }
        return Client('1', endpoint=endpoint, token=token)

    def create(self, name,
                template_file,
                env_file=None,
                format='json'):
        """ create heat stack with the given template and environment files """
        self.client.format = format
        tpl_files, template = template_utils.get_template_contents(template_file)
        env_files, env = template_utils.process_multiple_environments_and_files(env_paths=env_file)

        stack = self.client.stacks.create(stack_name=name,
                                   template=template,
                                   environment=env,
                                   files=dict(list(tpl_files.items()) + list(env_files.items())),
                                   parameters={})
        uid = stack['stack']['id']

        stack = self.client.stacks.get(stack_id=uid).to_dict()
        while stack['stack_status'] == 'CREATE_IN_PROGRESS':
            stack = self.client.stacks.get(stack_id=uid).to_dict()
            time.sleep(5)
        if stack['stack_status'] == 'CREATE_COMPLETE':
            return stack
        else:
            return False

    def list(self):
        """ list created stacks """
        fields = ['id', 'stack_name', 'stack_status', 'creation_time',
                  'updated_time']
        uids = []
        stacks = self.client.stacks.list()
        utils.print_list(stacks, fields)
        return obj_gen_to_dict(stacks)

    def delete(self, name):
        """ delete stack with the given name """
        self.client.stacks.delete(name)
        return self.list()

    def get_id(self, name):
        """ get stack id by name """
        stacks = self.client.stacks.list()
        while True:
            try:
                stack = stacks.next()
                if name == stack.stack_name:
                    return stack.id
            except StopIteration:
                break
                return False
def main():

    argument_spec = openstack_argument_spec()
    argument_spec.update(dict(
            stack_name              = dict(required=True),
            template                = dict(default=None),
            environment_files       = dict(default=None, type='list'),
            state                   = dict(default='present', choices=['absent', 'present']),
            tenant_name             = dict(default=None),
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    state = module.params['state']
    stack_name = module.params['stack_name']
    template = module.params['template']
    environment_files = module.params['environment_files']
    kwargs = {
                'username':  module.params['login_username'],
                'password':  module.params['login_password'],
                'tenant_name':  module.params['tenant_name'],
                'auth_url':  module.params['auth_url']
            }

    stack = Stack(kwargs)
    if module.params['state'] == 'present':
        stack_id = stack.get_id(stack_name)
        if not stack_id:
            stack = stack.create(name=stack_name,
                                        template_file=template,
                                        env_file=environment_files)
            if not stack:
                module.fail_json(msg="Failed to create stack")
            module.exit_json(changed = True, result = "Created" , stack = stack)
        else:
            module.exit_json(changed = False, result = "success" , id = stack_id)
    else:
        stack_id = stack.get_id(stack_name)
        if not stack_id:
            module.exit_json(changed = False, result = "success")
        else:
            stack.delete(stack_name)
            module.exit_json(changed = True, result = "deleted")

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
if __name__ == '__main__':
    main()
