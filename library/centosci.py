#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2015, Attila Darazs <adarazs@redhat.com>
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
module: centosci
version_added: "1.6"
short_description: Allocate and release hosts on the CentOS CI environment
description:
   - Allocate and release hosts on the CentOS CI environment
'''

EXAMPLES = '''
# Allocate and release hosts on the CentOS CI environment
- centosci:
'''

import os
import urllib2


def get_hosts(url, key, ver, arch, count):
    url_elements = [url, "Node/get",
                    "?key=", key,
                    "&arch=", arch,
                    "$ver=", ver,
                    "&i_count=", count]
    req = urllib2.Request(''.join(url_elements))
    req.add_header('Accept', 'application/json')
    try:
        result = urllib2.urlopen(req)
    except urllib2.URLError, e:
        return {'failed': True,
                "msg": "API call failed. " +
                       "url: " + ''.join(url_elements) +
                       "reason: " + str(e.reason)}
    raw_data = result.read()
    try:
        data = json.loads(raw_data)
    except ValueError:
        return {'failed': True,
                "msg": "Can't parse reply from the server as JSON. "
                       "Reply was: " + raw_data}
    if len(data["hosts"]) != int(count):
        return {'failed': True,
                "msg": "Mismatch between requested and issued host count."}
    host_list = [{"name": "host" + str(i),
                  "hostname": data["hosts"][i]}
                 for i in xrange(len(data["hosts"]))]
    return {"changed": True,
            "hosts": host_list,
            "ssid": data["ssid"]}


def return_hosts(url, type_, key, ssid):
    url_elements = [url, "Node/", type_,
                    "?key=", key,
                    "&ssid=", ssid]
    try:
        urllib2.urlopen(''.join(url_elements))
    except urllib2.URLError, e:
        return {'failed': True,
                "msg": "API call failed. "
                       "Reason: " + str(e.reason)}
    return {"changed": True}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            request=dict(default='get', choices=['get', 'done', 'fail'], type='str'),
            url=dict(required=True, type='str'),
            # following are options for get
            ver=dict(default="7", type='str'),
            arch=dict(default='x86_64', choices=['x86_64', 'i386']),
            count=dict(default='1', type='str'),
            # needed for done or fail
            ssid=dict(default=None, type='str')
        )
    )
    key = os.environ.get('PROVISIONER_KEY')
    if key is None:
        module.fail_json(msg="Set the PROVISIONER_KEY environment variable.")
    if module.params["request"] == "get":
        result = get_hosts(module.params["url"],
                           key,
                           module.params["ver"],
                           module.params["arch"],
                           module.params["count"])
    else:
        result = return_hosts(module.params["url"],
                              module.params["request"],
                              key,
                              module.params["ssid"])
    module.exit_json(**result)

# see http://docs.ansible.com/developing_modules.html#common-module-boilerplate
from ansible.module_utils.basic import *
main()
