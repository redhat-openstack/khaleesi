#!/usr/bin/env python
from urlparse import urlparse

# (c) 2016, Gabriele Cerami <gcerami@redhat.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
author: Gabriele Cerami
module: urlparse
short_description: a module that uses urlparse to extract elements from a url
description:
    - The module parses url and register some information as facts
    - prefixed with the chosen prefix
options:
    facts_prefix:
        description:
            - the prefix with which the facts will
            - be registered
        required: false
        default: ''
    url:
        description:
            - the url to parse
        required: true
'''

def main():
    module = AnsibleModule(
        argument_spec = dict(
            url           = dict(required=True),
            facts_prefix  = dict(default='', required=False)
        )
    )

    facts = {}
    parsed_url = urlparse(module.params['url'])
    facts_prefix = module.params['facts_prefix']
    hostname_factname = '%sip' % facts_prefix
    port_factname = '%sport' % facts_prefix

    facts[hostname_factname] = parsed_url.hostname
    facts[port_factname] = parsed_url.port

    module.exit_json(changed=True, ansible_facts=facts)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
