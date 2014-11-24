#!/usr/bin/python

# (c) 2014, Red Hat, Inc.
# Written by Luigi Toscano <ltoscano@redhat.com>
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
module: product_snapshot_data
version_added: "1.7"
short_description: Get the data for RDO/RHELOSP builds
description:
   - Get the OpenStack snapshot type (whether puddle/poddle) and versions. This is tied to the way builds are produced for RDO/RHELOSP snasphosts.
'''

EXAMPLES = '''
# Get the snapshot type and version
- product_snapshot_data:
'''

import logging
import re
import urllib2
import subprocess

PUDDLE_CHANGELOG_VER_RE = re.compile(r'NEW DIRECTORY: .+\/([0-9]{4}-[0-9]{2}-[0-9]{2}\..)\/.+')
PUDDLE_URL_VER_RE = re.compile(r'http.+\/([0-9]{4}-[0-9]{2}-[0-9]{2}\..|latest)\/')

# Just for debugging issue, not for normal usage
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class NotFoundException(Exception):
    """ Internal exception """
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return repr(self.reason)


def _get_openstack_repo():
    """ Get the repository of the OpenStack packages, checking the location
            of the python-keystoneclient package """
    cmd = 'repoquery -q --qf="%{location}" --show-duplicates python-keystoneclient'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout_data, stderr_data) = proc.communicate()
    stdout_data = stdout_data.strip()
    if len(stderr_data) != 0 or len(stdout_data) == 0:
        raise NotFoundException('No repository found for the tested package (python-keystoneclient)')
    # higher priority to poodle repository, if available, as it is enabled
    # only for poodles while the other one is always enabled
    repos = stdout_data.split()
    found_repo = repos[0]
    for repo in repos:
        if '/poodle' in repo:
            found_repo = repo
            break
    return found_repo

def _get_snap_ver_from_mirrorurl(repo_url):
    """ Get the puddle/poodle version for the specified mirror URL """
    matched = PUDDLE_URL_VER_RE.match(repo_url)
    if matched:
        return matched.groups()[0]
    raise NotFoundException('Puddle/poodle version not matched in repository URL %s' % (repo_url))

def _get_snap_ver_from_changelog(url):
    """ Get the version from the changelog file """
    LOGGER.debug('URL: %s:', url)
    req = urllib2.Request(url)
    error_message = 'Unknown error'
    try:
        snap_f = urllib2.urlopen(req)
        for c_line in snap_f.readlines():
            matched = PUDDLE_CHANGELOG_VER_RE.match(c_line.strip())
            if matched:
                snapshot_type = 'puddle'
                if '/poodle' in c_line:
                    snapshot_type = 'poodle'
                return (snapshot_type, matched.groups()[0])
    except Exception, err:
        error_message = err
    raise NotFoundException(error_message)

def _get_puddle_version():
    """ Get the snapshot version and type (puddle/poodle) """
    repo_url = _get_openstack_repo()
    LOGGER.debug('REPO_URL: %s', repo_url)
    ver = _get_snap_ver_from_mirrorurl(repo_url)
    LOGGER.debug('VERSION: %s:', ver)
    ver_pat = r'/{0}/'.format(ver)
    LOGGER.debug('VERSION_PATTERN: %s:', ver_pat)
    base_snapshot_url = repo_url[:repo_url.find(ver_pat) + len(ver_pat)]
    LOGGER.debug('BASE_SNAPSHOT_URL: %s:', base_snapshot_url)
    (s_type, s_ver) = _get_snap_ver_from_changelog(base_snapshot_url + 'logs/changelog.log')
    return (s_type, s_ver)

def main():
    """ Main """
    module = AnsibleModule(
        argument_spec = dict()
    )

    try:
        version_data = _get_puddle_version()
        ansible_facts = {
            'product_snapshot_type': version_data[0],
            'product_snapshot_version': version_data[1]
        }
        module.exit_json(changed=True, ansible_facts=ansible_facts)
    except NotFoundException, err:
        module.fail_json(msg='Error retrieving the snapshot type/version: %s' % (err))

from ansible.module_utils.basic import *
main()
