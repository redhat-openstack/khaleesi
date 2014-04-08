#! /usr/bin/env python

"""
Settings.py is a scripts that generates a settings.yml for khaleesi from various settings sources.
Settings sources can specify variables directly or can define mappings.Variables will be generated
from mapping in exchange for a input parameter.

For a settings.yml to be successfully generated, all of the basic parameters must be specified
(there are no default values for these)

installer
product
productrelease
productreleaserepo
distribution
distrorelease
topology
networking
testsuite

The parameters can be specified from command line arguments, from environment variables, or passing a
job name from command line, following these criteria

If a job name is specified, parameters are desumed from the name.
Environment variables, when present,  will override those in job name
Specific command line arguments (ex --installer), if present,  will override job-name and environment variables.

Specifying a job name is the easiest way the set the basic parameter, but the job name must follow
the standard naming convention

Additionally, these command line arguments are required to generate the settings.
--site
--output-settings
--settings-path

Generic variable handling routines are offered
--update-variable
--set-variables
--delete-variables
--create-variables

More the one of any of these arguments can be specified

For example:
--update-variables ssh_private_key=rdo-ci.pem --update-variables ssh_key_name=rdo-ci --create-variables warp=9

is a valid piece of command line.

=== Settings file generation.

The script will expect to find these directories under settings-path:

tempest/ will contain files with tmpest related variables and mappings
sites/ will contain ymml files with site related variables and mappings
builds/ will contain yaml files with generic build related variables

when started, the script will try to load starting parameters from
builds/defaults.yml
tempest/defaults.yml

into a mixed dict/list data tree that will represent the base settings

No error will be returned if any of these files is not present

the variables and values in the  mixed dict/list can be addressed with keypaths. So a
variable loaded from this yaml snippet

config:
    installer: packstack

can be fetched with the string 'config.installer' or set with the string 'config.installer=packstack'

Then the script will try to get the principal parameters and load variables from

builds/<variant-name>.yml
tempest/<testsuite>.yml
sites/<site>.yml

variables from these files will override the ones in the defaults files.

Then it will manipulate the data tree, generating legacy variables:
    - from the mappings using a combination of variable and principal parameters (ex image_id will be searched in the image mapping using a combination of site, distribution and distribution version)
    - from loaded values in different subtrees
    - from  environment variables

All the mappings should the be deleted from the data tree, as they're not actual variables.

In the end,  generic command line arguments will be applied, if present (Ex --update-variables) that will override everything else
"""

import yaml
import os
import argparse
import sys
import urllib2
import stat
import copy
import string
#for debugging
import pprint
import logging

# not yet used
#from novaclient.v1_1 import client as os_novaclient


class KeyPathError(Exception):

    def __init__(self, keypath, details):
        self.keypath = keypath
        self.details = details

    def __str__(self):
        if self.keypath is None:
            return "Key path error: %s" % (self.details)
        else:
            return "Key path error in %s (%s) against data subtree %s: $s" % (
                self.keypath.keypath_string,
                self.keypath.match_depth_segment,
                pprint.pformat(self.keypath.pointer),
                self.details)


class KeyPath(object):
    """
    A keypath is a string that defines a
    list of keys and optionally an assigned value
    Ex. "a.b.c=0"

    keys may be string or integers

    The main purpose of a keypath is to address a subtree on
    a mixed dict/list data structure.
    string keys refer to dict parts of the data structure
    integer keys refer to list parts of the data structure
    A class is required to maintain information related to the keypath
    presence inside the data structure. If it's present, if the optional
    value in the keypath string matches the one on the data structure.
    A method to search a keypath inside a mixed dict/list is also implemented.
    """

    def __init__(self, keypath_fullstring, values=None, select_function=None):
        if keypath_fullstring is None:
            raise KeyPathError(None, "Null keypath string")
        self.keypath_string = keypath_fullstring.split('=')[0]
        logger.debug("Initializing keypath " + str(self) + " with full string: " + str(keypath_fullstring))
        logger.debug(str(self) + " path part " + self.keypath_string)
        self.keypathlist = self.keypath_string.split('.')
        # replace all : with .
        self.keypathlist = map(string.replace,
                               self.keypathlist,
                               (':')*len(self.keypathlist),
                               ('.')*len(self.keypathlist))
        # The override function get a tuple of
        # values and returns a single value that may or may be not
        # one of the values of the tuple
        self.select_function = select_function

        try:
            stringvalue = keypath_fullstring.split('=')[1]
        except IndexError:
            stringvalue = None

        if stringvalue and values:
            raise Exception("Values for keypath can be specified either by string or value parameter, but not both")
        if stringvalue:
            self.set_value(stringvalue)
        elif values:
            self.set_value(values)
        else:
            self.set_value(None)

        logger.debug( str(self) + " value part " + str(self.value))
        self.match_depth = None
        self.match_depth_segment = None
        self.path_match = False
        self.value_match = False
        self.parentpointer = None
        self.pointer = None

    def set_value(self, values):
        if type(values) is tuple:
            if self.select_function:
                self.value = self.select_function(*values)
            else:
                self.value = None
        else:
            self.value =  values

    def __str__(self):
        return self.keypath_string

    def search_in(self, data):
        """
        search for keypath inside a mixed dict/list data structure
        keypath is navigated and compared against the data.
        match_depth records the position of the last key matching the data
        if all keypath is matched, path_match is set to True then value is compared too if specified
        pointer contains a pointer to data referenced by the last key in keypath
        parentpointer contains a pointer to the upper level data structure
        """

        self.parentpointer = data
        self.pointer = data
        for index, segment in enumerate(self.keypathlist):
            tmppointer = self.parentpointer
            self.parentpointer = self.pointer

            if type(self.pointer) is dict:
                try:
                    self.pointer = self.pointer[segment]
                except KeyError:
                    self.parentpointer = tmppointer
                    return
            elif type(self.pointer) is list:
                try:
                    self.pointer = self.pointer[int(segment)]
                except (TypeError, IndexError):
                    self.parentpointer = tmppointer
                    return

            self.match_depth = index
            self.match_depth_segment = segment

        self.path_match = True
        if self.value:
            self.value_match = (self.value == self.pointer)

    def structurize(self, depth):
        """
        converts keypath starting from "depth" position
        to a mixed dict/list data structure
        from a.b.c=value to {'a': {'b': {'c': 'value'}}}
        from a.0.c=value to {'a': [{'c': 'value'}]}
        This is done to simplyfy inseting subtree on
        the mixed dict/list data structure
        """
        # TODO: it should be more readable and simpler implementing
        # this function recursively
        rgrow_dict = self.value
        tmp_keypathlist = copy.deepcopy(self.keypathlist)
        while tmp_keypathlist[depth:]:
            try:
                tmp_dataroot = tmp_keypathlist[-2]
            except IndexError:
                tmp_dataroot = 'temporarydataroot'
            if len(tmp_keypathlist) == 1:
                index = 0
            else:
                index = -1
            try:
                key = int(tmp_keypathlist[index])
            except ValueError:
                key = tmp_keypathlist[index]
            if type(key) is int:
                locals()[tmp_dataroot] = []
                locals()[tmp_dataroot].append(rgrow_dict)
            elif type(key) is str:
                locals()[tmp_dataroot] = {}
                locals()[tmp_dataroot][key] = rgrow_dict
            rgrow_dict = locals()[tmp_dataroot]
            tmp_keypathlist.pop()

        return rgrow_dict


class Settings(object):
    """
    Setting class will contain the mixed dict/list data structure containing the
    settings and implement methods to manipulate data using keypaths and offering a
    CRUD interface
    """

    def __init__(self, data, select_function=None):
        self.data = data
        self.keypaths = {}
        self.keypath_max = 10
        if select_function:
            self.select_function = select_function

    def set_select_function(self, select_function):
        self.select_function = select_function

    def add_keypath(self, keypath_string, values):

        if keypath_string not in self.keypaths:
            keypath = KeyPath(keypath_string, values=values, select_function=self.select_function)
            # ugly garbage collection
            # since python 2.6 does not support orderedDict a random key will
            # be deleted
            if len(self.keypaths) > self.keypath_max:
                self.keypaths.popitem()
            self.keypaths[keypath_string] = keypath
        elif self.keypaths[keypath_string].value != values:
            self.keypaths[keypath_string].set_value(values)
        self.keypaths[keypath_string].search_in(self.data)

        return self.keypaths[keypath_string]

    def delete(self, keypath_string, values=None):
        """
        Delete a subtree in the settings referenced by a keypath string
        If value in the keypath is specified, delete only if value match the value in the settings
        """
        keypath = self.add_keypath(keypath_string, values)
        logger.debug("Deleting keypath: " + str(keypath.keypath_string) + " using value: " + str(keypath.value))
        if keypath.path_match:
            if keypath.value is not None:
                logger.debug("Value specified in keypath, deleting only if it matches the actual value")
                if not keypath.value_match:
                    raise KeyPathError(self.keypath, "Specified value does not match")
            overstructure = keypath.parentpointer
            if type(overstructure) is list:
                key = keypath.keypathlist[int(keypath.match_depth)]
            elif type(overstructure) is dict:
                key = keypath.keypathlist[keypath.match_depth]

            overstructure.pop(key)
            logger.debug("Deleting keypath: " + str(keypath.keypath_string)+ " deleted")
        else:
            raise KeyPathError(self.keypath, "Keypath does not exists")

    # XXX: if values is None (no values could be chosen from the tuple), do not perform any operation
    def create(self, keypath_string, values=None):
        """
        add a keypath with value to the settings only if it's not present
        """
        keypath = self.add_keypath(keypath_string, values)
        logger.debug("Creating keypath " + str(keypath.keypath_string + " using values " + str(keypath.value)))
        overstructure = keypath.parentpointer
        if keypath.path_match:
            raise KeyPathError(keypath, "path already exists")
        else:
            if keypath.match_depth is None:
                logger.debug("keypath does not match at all the structure " + str(self))
                # Keypath did not matched from root, structurize everything
                new_data = keypath.structurize(0)
                key = keypath.keypathlist[0]
                logger.debug("new data to attach to the root " + pprint.pformat(new_data))
                if type(overstructure) is dict:
                        overstructure.update(new_data)
                elif type(overstructure) is list:
                        overstructure.append(new_data)
            else:
                # Structurize everythin past last matched key
                new_data = keypath.structurize(keypath.match_depth + 1)
                key = keypath.keypathlist[keypath.match_depth]
                logger.debug("keypath partially match the structure " + str(self) + " until " + str(key))
                logger.debug("new data to attach to " + str(key) + " " + pprint.pformat(new_data))
                if type(overstructure[key]) is dict:
                        overstructure[key].update(new_data)
                elif type(overstructure[key]) is list:
                        overstructure[key] += new_data
        logger.debug("Creating keypath: " + str(keypath.keypath_string)+ " created")

    def update(self, keypath_string, values=None):
        """
        Alter the value of a paraameter only if exists
        """
        keypath = self.add_keypath(keypath_string, values)
        logger.debug("Updating keypath: " + str(keypath.keypath_string) + " with values " + str(keypath.value))
        if not keypath.path_match:
            raise KeyPathError(keypath, "path does not exist")
        elif keypath.value_match:
            logger.warning("keypath %s already set to %s" % (keypath.keypath_string, str(keypath.value)))
        else:
            overstructure = keypath.parentpointer
            new_data = keypath.structurize(keypath.match_depth)
            key = keypath.keypathlist[keypath.match_depth]
            if type(overstructure) is dict:
                    overstructure.update(new_data)
            elif type(overstructure) is list:
                    overstructure.append(new_data)
            logger.debug("Updating keypath: " + str(keypath.keypath_string)+ " updated")

    def set(self, keypath_string, values=None):
        """
        If a keypath does not exists, create it.
        If exists, update it
        """
        keypath = self.add_keypath(keypath_string, values)
        if keypath.path_match:
            self.update(keypath_string, values)
        else:
            self.create(keypath_string, values)

    def fetch(self, keypath_string, values=None):
        """
        get the value addressed by the keypath string
        any value provided with the keypath string will be ignored
        """
        keypath = self.add_keypath(keypath_string, values)
        logger.debug("Fetching keypath: " + keypath.keypath_string)
        # value will be ignored
        if keypath.value:
            logger.warning("specified value will be ignored")
        if keypath.path_match:
            logger.debug("Fetching keypath: " + keypath.keypath_string + " fetched value " + str(keypath.pointer))
            return keypath.pointer
        else:
            raise KeyPathError(self, "path does not exist")

    def batch_execute(self, keypaths, operation):
        """
        Executes a set of operation specified as dict or list of keypaths
        if dict is passed: keypath string as key, values as values.
        if list is passed: keypath full string is required as value
        example
            settings.batch_execute({ "keypath": value}, operation)
        """
        logger.debug("keypaths to batch " + str(operation) + ": " + str(keypaths) + "  type " + str(type(keypaths)))
        if type(keypaths) is dict:
            for keypath_string in keypaths:
                values = keypaths[keypath_string]
                self.__getattribute__(operation)(keypath_string, values=values)
        elif type(keypaths) is list:
            for keypath_string in keypaths:
                self.__getattribute__(operation)(keypath_string)


class Job(object):
    """
    Job class will handle the defaults of he job
    """
    _node_prefix_map = {
        "installer": {
            "foreman": "fore",
            "packstack": "pack",
            "tripleo": "trio"
        },
        "product": {
            "rdo": "rdo",
            "rhos": "rhos",
        },
        "productrelease": {
            "icehouse": "I",
            "havana": "H",
            "grizzly": "G",
        },
        "productreleaserepo": {
            "production": "prod",
            "stage": "sta",
            "testing": "test",
        },
        "distribution": {
            "centos": "C",
            "rhel": "R",
            "fedora": "F"
        },
        "distrorelease": {},
        "topology": {
            "aio": "a",
            "multinode": "m",
        },
        "networking": {
            "nova": "nova",
            "neutron": "neut",
            "ml2": "ml2",
        },
        "variant": {},
        "testsuite": {},
    }

    def generate_node_prefix(self, config):
        node_prefix = "{installer}-{product}-{productrelease}-{productreleaserepo}-{distribution}{distroversion}-{topology}-{networking}-{variant}".format(
            installer=self._node_prefix_map['installer'][config['installer']],
            product=self._node_prefix_map['product'][config['product']],
            productrelease=self._node_prefix_map['productrelease'][config['productrelease']],
            productreleaserepo=self._node_prefix_map['productreleaserepo'][config['productreleaserepo']],
            distribution=self._node_prefix_map['distribution'][config['distribution']],
            distroversion=config['distrorelease'].replace('.', ''),
            topology=self._node_prefix_map['topology'][config['topology']],
            networking=self._node_prefix_map['networking'][config['networking']],
            variant=config['variant'],
        )
        return node_prefix

    def choose_value(self, env_var_name, cli_var_name, keypath_string):
        """
        choose value for a keypath in this order
        - specific command line argument
        - environment variable
        - value from a specified keypath
        - None
        Value can then be overriden by a generic --var-{set,update,create,delete} cli arg
        """
        choices = "(" + str(env_var_name) + "," + str(cli_var_name) + "," + str(keypath_string) + "): "
        logger.debug("Choosing a value between cli parameter \'" + str(cli_var_name) + "\' env variable \'" +  str(env_var_name) + "\' and keypath string \'" + str(keypath_string) + "\'")
        rvalue = None
        if rvalue is None and cli_var_name is not None:
            try:
                logger.debug(choices +"Evaluating cli parameter")
                rvalue = self.args_parsed.__dict__[cli_var_name]
                if rvalue is not None:
                    logger.info(choices + "value: " + str(rvalue) + " from cli parameter: " + str(cli_var_name) + " selected")
            except KeyError:
                pass
        if rvalue is None and env_var_name is not None:
            try:
                logger.debug(choices+ "Evaluating env variable")
                rvalue = os.environ[env_var_name]
                logger.info(choices + "value: " + str(rvalue) + " from environment var: " + str(env_var_name) + " selected")
            except KeyError:
                pass
        if rvalue is None and keypath_string is not None:
            try:
                logger.debug(choices + "Evaluating keypath string")
                rvalue = self.settings.fetch(keypath_string)
                if rvalue is not None:
                    logger.info(choices + "value: " + str(rvalue) + " from keypath string: " + str(keypath_string) + " selected")
            except KeyPathError:
                pass
        if rvalue is None:
                logger.info( choices + "No valid values found")

        return rvalue

    def __init__(self, args_parsed):
        self.args_parsed = args_parsed

        self.settings = Settings({}, select_function=self.choose_value)
        self.settings.create('provision_site', values=('SITE', 'site', None))
        self.settings.create('job_name', values=('JOB_NAME', 'job_name', None))

        job_name = self.settings.fetch('job_name')

        if job_name is not None:
            job_name = job_name.split('_')
            job_name.reverse()
            # Unused
            framework = job_name.pop()
            installer = job_name.pop()
            product = job_name.pop()
            productrelease = job_name.pop()
            productreleaserepo = job_name.pop().replace('-repo', '')
            distroblock = job_name.pop()
            distribution = distroblock.split('-')[0]
            distrorelease = distroblock.split('-')[1]
            topology = job_name.pop()
            networking = job_name.pop()
            variant = job_name.pop().replace('-variant', '')
            testsuite = job_name.pop().replace('-tests', '')
            keypaths = {
                'config.installer': installer,
                'config.product': product,
                'config.productrelease': productrelease,
                'config.productreleaserepo': productreleaserepo,
                'config.distribution': distribution,
                'config.distrorelease': distrorelease,
                'config.topology': topology,
                'config.networking': networking,
                'config.variant': variant,
                'config.testsuite': testsuite,
            }
            self.settings.batch_execute(keypaths, 'create')
        self.settings_path = self.choose_value('SETTINGS_PATH', 'settings_path', None)

        # No defaults are possible for site

        build_settings_path = "%s%sbuilds%s%s.yml" % (
            self.settings_path, os.sep, os.sep, 'defaults')
        try:
            with open(build_settings_path) as build_settings_file:
                self.settings.create('build', values=yaml.load(build_settings_file))
        except IOError:
            pass

        tempest_settings_path = "%s%stempest%s%s.yml" % (
            self.settings_path, os.sep, os.sep, 'defaults')
        try:
            with open(tempest_settings_path) as tempest_settings_file:
                self.settings.create('tempest', values=yaml.load(tempest_settings_file))
        except IOError:
            pass


class Build(object):
    """
    Build class will handle build specific settings generation
    """

    def __init__(self, job, args):
        self.job = job
        self.args_parsed = args

        settingsdata = copy.deepcopy(job.settings.data)
        self.settings = Settings(settingsdata, select_function=self.choose_value)
        # Hack, updating settings with job.settings section values
        # SHOULD NOT be needed in deepened settings.yml
        # future version of settings should only require
        # self.settings = copy.deepcopy(job.settings)

        try:
            builddata = job.settings.fetch('build')
            self.settings.data.update(builddata)
        except KeyPathError:
            pass

        keypaths = {
            'config.installer': ('INSTALLER', 'installer', 'config.installer'),
            'config.product': ('PRODUCT', 'product', 'config.product'),
            'config.productrelease': ('PRODUCTRELEASE', 'productrelease', 'config.productrelease'),
            'config.productreleaserepo': ('PRODUCTRELEASEREPO', 'productreleaserepo', 'config.productreleaserepo'),
            'config.distribution': ('DISTRIBUTION', 'distribution', 'config.distribution'),
            'config.distrorelease': ('DISTRORELEASE', 'distrorelease', 'config.distrorelease'),
            'config.topology': ('TOPOLOGY', 'topology', 'config.topology'),
            'config.networking': ('NETWORKING', 'networking', 'config.networking'),
            'config.variant': ('VARIANT', 'variant', 'config.variant'),
            'config.testsuite': ('TESTS', 'testsuite', 'config.testsuite'),

            # for backwards compatibility
            'config.netplugin': ('NETPLUGIN', 'networking', 'config.networking'),
            'config.version': ('PRODUCTRELEASE', 'productrelease', 'config.productrelease'),
            'config.repo': ('PRODUCTRELEASEREPO', 'productreleaserepo', 'config.productreleaserepo'),
        }
        self.settings.batch_execute(keypaths, 'set')

        self.site_settings_filename = self.settings.fetch('provision_site')
        self.tempest_settings_filename = self.settings.fetch('config.testsuite')
        self.build_settings_filename = self.settings.fetch('config.variant')

        # load build specific conf
        site_settings_path = "%s%ssites%s%s.yml" % (
            self.job.settings_path, os.sep, os.sep, self.site_settings_filename)
        try:
            with open(site_settings_path) as site_settings_file:
                self.settings.set('site', values=yaml.load(site_settings_file))
        except IOError:
            pass

        build_settings_path = "%s%sbuilds%s%s.yml" % (
            self.job.settings_path, os.sep, os.sep, self.build_settings_filename)
        try:
            with open(build_settings_path) as build_settings_file:
                self.settings.set('build', values=yaml.load(build_settings_file))
        except IOError:
            pass

        tempest_settings_path = "%s%stempest%s%s.yml" % (
            self.job.settings_path, os.sep, os.sep, self.tempest_settings_filename)
        try:
            with open(tempest_settings_path) as tempest_settings_file:
                self.settings.set('tempest', values=yaml.load(tempest_settings_file))
        except IOError:
            pass

    def generate_settings(self):
        distribution = self.settings.fetch('config.distribution')
        distrorelease = self.settings.fetch('config.distrorelease').replace('.', ':')
        product = self.settings.fetch('config.product')
        productrelease = self.settings.fetch('config.distrorelease').replace('.', ':')

        keypaths = {
            'packstack_int': 'whayutin',
            'config.verbosity': ['info', ],

            'os_auth_url': ('OS_AUTH_URL', None, 'site.controller.auth-url'),
            'os_username': ('OS_USERNAME', None, 'site.controller.username'),
            'os_password': ('OS_PASSWORD', None, 'site.controller.password'),
            'os_tenant_name': ('OS_TENANT_NAME', None, 'site.controller.tenant_name'),
            'os_network_type': ('OS_NETWORK_TYPE', None, 'site.controller.network-type'),

            # instance settings
            'image_id': ('IMAGE_ID', None, 'site.images.' + distribution + '.' + distrorelease + '.id'),
            'remote_user': ('REMOTE_USER', None, 'site.images.' + distribution + '.' + distrorelease + '.remote-user'),
            'ssh_private_key': ('KEY_FILE', None, 'site.instances.key_filename'),
            'ssh_private_key_remote': ('KEY_FILE_REMOTE', None, 'site.instances.key_remote_url'),
            'ssh_key_name': ('KEY_NAME', None, 'site.instances.key_name'),
            'flavor_id': ('FLAVOR_ID', None, 'site.instances.flavors.default.id'),
            'flavor_name': ('FLAVOR_NAME', None, 'site.instances.flavors.default.name'),
            'floating_network_name': ('FLOATING_NETWORK_NAME', None, 'site.networks.floating.name'),
            'tempest_image_id': ('TEMPEST_IMAGE_ID', None, 'site.images.tempest.id'),
            'tempest_flavor_id': ('TEMPEST_FLAVOR_ID', None, 'site.instances.flavors.tempest.id'),
            'tempest_flavor_name': ('TEMPEST_FLAVOR_NAME', None, 'site.instances.flavors.tempest.name'),
            'tempest_remote_user': ('TEMPEST_REMOTE_USER', None, 'site.images.tempest.remote-user'),
            'foreman_image_id': ('FOREMAN_IMAGE_ID', None, 'site.images.foreman.id'),
            'foreman_flavor_id': ('FOREMAN_FLAVOR_ID', None, 'site.instances.flavors.foreman.id'),
            'foreman_flavor_name': ('FOREMAN_FLAVOR_NAME', None, 'site.instances.flavors.foreman.name'),
            'foreman_remote_user': ('FOREMAN_REMOTE_USER', None, 'site.images.foreman.remote-user'),
            # tempest overrides
            'tempest.revision': (None, None ,'tempest.revisions.' + product + '.'+ productrelease),
            'tempest.tempest_test_name' : ('TEMPEST_TEST_NAME', None, 'tempest.test_name'),
        }
        self.settings.batch_execute(keypaths, 'create')
        keypaths = {
            # build overrides
            'node_prefix': ('NODE_PREFIX', None, 'node_prefix'),
            'wait_for_boot': ('WAIT_FOR_BOOT', None, 'build.wait_for_boot'),
            'update_rpms_tarball': ('UPDATE_RPMS_TARBALL', None, 'build.update_rpms_tarball'),
            'selinux': ('SELINUX', None, 'selinux')
        }
        self.settings.batch_execute(keypaths, 'set')
        # More network settings
        #
        # we can use novaclient to check id->name translation
        #novaclient = os_novaclient.Client(os_username, os_password, os_tenant_name, os_auth_url, service_type='compute')
        #net = novaclient.networks.find(id=network['id'])
        #net_names.append(net.label)
        network_ids = []
        network_names = []
        for seq, network in enumerate(self.settings.fetch('site.networks.internal')):
            # skip net 0
            if seq != 0:
                self.settings.create('net_' + str(seq) + '_name', values=('NET_' + str(seq) + '_NAME',  None, 'site.networks.internal.' + str(seq) + '.name'))
                network_names.append(self.settings.fetch('net_' + str(seq) + '_name'))
                network_ids.append({'net-id': os.getenv('NET_' + str(seq),  network['id'])})
        self.settings.create('network_ids', values=network_ids)
        self.settings.create('network_names', values=network_names)

        node_prefix = self.job.generate_node_prefix(self.settings.fetch('config'))
        self.settings.update('node_prefix', values=node_prefix)
        # Final overrides
        # cli generic manipulation parameters (set,delete,create,update)
        # have priority over all other way of retrieving settings
        logger.debug("Processing generic overrides")
        if self.args_parsed.set_variables:
            logger.debug("Processing generic set: " + str(self.args_parsed.set_variables))
            self.settings.batch_execute(self.args_parsed.set_variables, 'set')
        if self.args_parsed.delete_variables:
            logger.debug("Processing generic delete: " + str(self.args_parsed.delete_variables))
            self.settings.batch_execute(self.args_parsed.delete_variables, 'delete')
        if self.args_parsed.create_variables:
            logger.debug("Processing generic create: " + str(self.args_parsed.create_variables))
            self.settings.batch_execute(self.args_parsed.create_variables, 'create')
        if self.args_parsed.update_variables:
            logger.debug("Processing generic update: " + str(self.args_parsed.update_variables))
            self.settings.batch_execute(self.args_parsed.update_variables, 'update')

        # Cleanup
        # remove tempest revision mappings
        self.settings.delete('tempest.revisions')
        # needed by the previous hacks
        self.settings.delete('build')
        self.settings.delete('site')

    def choose_value(self, env_var_name, cli_var_name, keypath_string):
        """
        choose value for a keypath in this order
        - specific command line argument
        - environment variable
        - value from a specified keypath
        - None
        Value can then be overriden by a generic --var-{set,update,create,delete} cli arg
        """
        choices = "(" + str(env_var_name) + "," + str(cli_var_name) + "," + str(keypath_string) + "): "
        logger.debug("Choosing a value between cli parameter \'" + str(cli_var_name) + "\' env variable \'" +  str(env_var_name) + "\' and keypath string \'" + str(keypath_string) + "\'")
        rvalue = None
        if rvalue is None and cli_var_name is not None:
            try:
                logger.debug(choices +"Evaluating cli parameter")
                rvalue = self.args_parsed.__dict__[cli_var_name]
                if rvalue is not None:
                    logger.info(choices + "value: " + str(rvalue) + " from cli parameter: " + str(cli_var_name) + " selected")
            except KeyError:
                pass
        if rvalue is None and env_var_name is not None:
            try:
                logger.debug(choices+ "Evaluating env variable")
                rvalue = os.environ[env_var_name]
                logger.info(choices + "value: " + str(rvalue) + " from environment var: " + str(env_var_name) + " selected")
            except KeyError:
                pass
        if rvalue is None and keypath_string is not None:
            try:
                logger.debug(choices + "Evaluating keypath string")
                rvalue = self.settings.fetch(keypath_string)
                if rvalue is not None:
                    logger.info(choices + "value: " + str(rvalue) + " from keypath string " + str(keypath_string) + " selected")
            except KeyPathError:
                pass
        if rvalue is None:
                logger.info( choices + "No valid values found")

        return rvalue

    def retrieve_key_file(self):
        url = self.settings.fetch('ssh_private_key_remote')
        key_filename = self.settings.fetch('ssh_private_key')
        if url:
            response = urllib2.urlopen(url)
            key = response.read()
            with open(key_filename, "w") as key_file:
                key_file.write(key)
            os.chmod(key_filename, stat.S_IRUSR | stat.S_IWUSR)

    def write_settings(self, output_settings_path):
        with open(output_settings_path, "w") as output_settings_file:
            output_settings_file.write("# job config\n")
            output_settings_file.write(yaml.safe_dump(self.settings.data,
                                                 default_flow_style=False))


def parse_args(args):
    parser = argparse.ArgumentParser(description="Load khaleesi build settings")
    parser.add_argument("--job-name",
                        dest="job_name",
                        help="",)
    parser.add_argument("-o", "--output-settings",
                        dest="output_settings_path",
                        required=True,
                        help="Path for the output settings file")
    parser.add_argument("-s", "--site",
                        dest="site",
                        required=True,
                        help="Site where the build is launched")
    parser.add_argument("-P", "--settings-path",
                        dest="settings_path",
                        required=True,
                        default="../khaleesi-settings",
                        help="The path where khaleesi settings are")
    parser.add_argument("--product",
                        dest="product",
                        help="The product to test. Supported are rdo, rhos",)
    parser.add_argument("--productrelease",
                        dest="productrelease",
                        help="The release of the product to test (ex. Icehouse)")
    parser.add_argument("--productreleaserepo",
                        dest="productreleaserepo",
                        help="The name of the repo to test the product from (Ex. production)",)
    parser.add_argument("--installer",
                        dest="installer",
                        help="The name of the installer (ex. packstack)",)
    parser.add_argument("--distribution",
                        dest="distribution",
                        help="The distribution on which the product shall be tested (ex. centos)",)
    parser.add_argument("--distrorelease",
                        dest="distrorelease",
                        help="The release of the distribution (Ex. 6.5)",)
    parser.add_argument("--topology",
                        dest="topology",
                        help="The name of the topology to be created and tested (Ex allinone)",)
    parser.add_argument("--networking",
                        dest="networking",
                        help="The name of the networkin plugin to be used (Ex. nova)",)
    parser.add_argument("--variant",
                        dest="variant",
                        help="A container name for all the parameters that don't fit on the job name (Ex. basic will use all the default values for the build)",)
    parser.add_argument("--testsuite",
                        dest="testsuite",
                        help="A container name that defines the test to be used and test related variables",)
    parser.add_argument("--ignore-parameters-from",
                        dest="ignore_from",
                        help="",)
    parser.add_argument("--set-variable",
                        action='append',
                        dest="set_variables",
                        help="",)
    parser.add_argument("--delete-variable",
                        action='append',
                        dest="delete_variables",
                        help="",)
    parser.add_argument("--update-variable",
                        action='append',
                        dest="update_variables",
                        help="",)
    parser.add_argument("--create-variable",
                        action='append',
                        dest="create_variables",
                        help="",)
    parser.add_argument("--log-level",
                        dest="log_level",
                        default="INFO",
                        help="Set logging level [INFO, WARNING, DEBUG]",)
    args_parsed, unknown = parser.parse_known_args(args)

    return args_parsed


def setup_logging(args_parsed):
    FORMAT = '%(filename)s(%(levelname)s):%(funcName)s:%(lineno)s: %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('settings')
    if args_parsed.log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif args_parsed.log_level == 'INFO':
        logger.setLevel(logging.INFO)


    return logger


def main(args):
    global logger
    args_parsed = parse_args(args)
    logger = setup_logging(args_parsed)

    current_job = Job(args_parsed)

    # colors:
    #  print "\033[3" + str(number) + ";1m" + string

    current_build = Build(current_job, args_parsed)
    current_build.generate_settings()
    current_build.retrieve_key_file()
    current_build.write_settings(args_parsed.output_settings_path)

if __name__ == '__main__':
    main(sys.argv)
