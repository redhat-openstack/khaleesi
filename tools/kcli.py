#!/usr/bin/env python
import argparse
import os
import subprocess
import sys


PATH_TO_PLAYBOOKS = os.path.join(os.getcwd(), "playbooks")
VERBOSITY = 2
HOSTS_FILE = "hosts"
LOCAL_HOSTS = "local_hosts"
KSGEN_SETTINGS_YML = "ksgen_settings.yml"

PROVISION = "provision"
PLAYBOOKS = [PROVISION, "install", "test"]


def file_exists(parser, filename):
    if not os.path.exists(filename):
        parser.error("The file %s does not exist!" % filename)
    return filename


def parser_init():
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings",
                        default=KSGEN_SETTINGS_YML,
                        type=lambda x: file_exists(parser, x),
                        help="settings file to use. default: %s"
                             % KSGEN_SETTINGS_YML)
    parser.add_argument("--provision", action="store_true",
                        # default=False,
                        help="provision fresh nodes from server")
    parser.add_argument("--install", action="store_true",
                        # default=False,
                        help="install Openstack on nodes")
    parser.add_argument("--test", action="store_true",
                        # default=False,
                        help="execute tests")
    return parser.parse_args()


def verbosity(level=VERBOSITY):
    if level:
        return "-" + "v" * level
    return ""


def execute_ansible(playbook, settings):
    hosts = LOCAL_HOSTS if playbook == PROVISION else HOSTS_FILE
    playbook += ".yml"
    path_to_playbook = os.path.join(PATH_TO_PLAYBOOKS, playbook)
    arguments = [verbosity(), "--extra-vars", "@" + settings,
                 "-i", hosts,
                 path_to_playbook]
    subprocess.call(args=arguments,
                    executable="ansible-playbook")


def main():
    args = parser_init()
    settings = args.settings
    playbooks = [p for p in PLAYBOOKS if getattr(args, p)]
    if not playbooks:
        raise Exception("No playbook to execute (%s)" % PLAYBOOKS)
    for playbook in (p for p in PLAYBOOKS if getattr(args, p)):
        execute_ansible(playbook, settings)

if __name__ == '__main__':
    sys.exit(main())
