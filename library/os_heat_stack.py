#!/usr/bin/python
#coding: utf-8 -*-

try:
    import shade
    from time import sleep
    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False

DOCUMENTATION = '''
---
module: os_heat_stack
short_description: Add/Remove Heat Stack
extends_documentation_fragment: openstack
version_added: "2.0"
author: "Mathieu Bultel (matbu)"
description:
   - Add or Remove a Stack to an OpenStack Heat
options:
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     required: false
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
requirements:
    - "python >= 2.6"
    - "shade"
'''

EXAMPLES = '''
# Create a stack with given template and environment files
'''

def _create_stack(module, stack, cloud):
    try:
        stack = cloud.create_stack(module.params['stack_name'],
                                   template_file=module.params['template'],
                                   files=module.params['environment_files'])

        stack = cloud.get_stack(stack['stack']['id'], None)
        while stack['stack_status'] == 'CREATE_IN_PROGRESS':
            stack = cloud.get_stack(stack['id'])
            sleep(5)
        if stack['stack_status'] == 'CREATE_COMPLETE':
            return stack
        else:
            module.fail_json(msg = "Failure in creating stack: ".format(stack))
    except shade.OpenStackCloudException as e:
        module.fail_json(msg=e.message)

def _system_state_change(module, stack, cloud):
    state = module.params['state']
    if state == 'present':
        if not stack:
            return True
    if state == 'absent' and stack:
        return True
    return False

def main():

    argument_spec = openstack_full_argument_spec(
        stack_name=dict(required=True),
        template=dict(default=None),
        environment_files=dict(default=None, type='dict'),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           **module_kwargs)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    state = module.params['state']
    stack_name = module.params['stack_name']
    template = module.params['template']
    environment_files = module.params['environment_files']

    # Check for required parameters when state == 'present'
    if state == 'present':
        for p in ['stack_name', 'template']:
            if not module.params[p]:
                module.fail_json(msg='%s required with present state' % p)

    try:
        cloud = shade.openstack_cloud(**module.params)
        stack = cloud.get_stack(stack_name)

        if module.check_mode:
            module.exit_json(changed=_system_state_change(module, stack,
                                                          cloud))

        if state == 'present':
            if not stack:
                stack = _create_stack(module, stack, cloud)
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed,
                             stack=stack,
                             id=stack['id'])
        elif state == 'absent':
            if not stack:
                changed = False
            else:
                changed = True
                cloud.delete_stack(stack_name)
            module.exit_json(changed=changed)

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=e.message)

# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
if __name__ == '__main__':
    main()
