import os
import ConfigParser

import bugzilla

from ansible import utils


class LookupModule(object):

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def bugzilla_load_config_file(self):
        p = ConfigParser.SafeConfigParser()
        path1 = os.getcwd() + "/bugzilla.ini"
        path2 = os.path.expanduser(
            os.environ.get('ANSIBLE_CONFIG', "~/bugzilla.ini"))
        path3 = "/etc/ansible/bugzilla.ini"

        if os.path.exists(path1):
            p.read(path1)
        elif os.path.exists(path2):
            p.read(path2)
        elif os.path.exists(path3):
            p.read(path3)
        else:
            return None
        return p

    def run(self, terms, inject=None, **kwargs):
        self.config = self.bugzilla_load_config_file()
        url = self.config.get('bugzilla', 'url')
        username = self.config.get('bugzilla', 'username')
        password = self.config.get('bugzilla', 'password')
        open_statuses = self.config.get('bugzilla', 'open_statuses'
                                        ).upper().split(',')

        bz = bugzilla.Bugzilla(url=url)
        bz.login(username, password)

        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)

        ret = []
        for term in terms:
            bug = bz.getbugsimple(term)
            status = str(bug).split(None, 2)[1]
            if status in open_statuses:
                should_run = "yes"
            else:
                should_run = "no"
            ret.append(should_run)
        return ret
