#!/usr/bin/env python
import argparse
import os
import sys

import ansible.playbook
from ansible import callbacks
from ansible import color as ansible_color
from ansible import inventory
from ansible import utils

# ansible-playbook https://github.com/ansible/ansible/blob/devel/bin/ansible-playbook

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
    parser.add_argument('-i', '--inventory',
                        default=None,
                        type=lambda x: file_exists(parser, x),
                        help="Inventory file to use. "
                             "Default: {lcl}. "
                             "NOTE: to reuse old environment use {host}".
                        format(lcl=LOCAL_HOSTS, host=HOSTS_FILE))
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

    args = parser.parse_args()

    playbooks = [p for p in PLAYBOOKS if getattr(args, p)]
    if not playbooks:
        parser.error("No playbook to execute (%s)" % PLAYBOOKS)
    return args


# From ansible-playbook
def colorize(lead, num, color):
    """ Print 'lead' = 'num' in 'color' """
    if num != 0 and color is not None:
        return "%s%s%-15s" % (ansible_color.stringc(lead, color),
                              ansible_color.stringc("=", color),
                              ansible_color.stringc(str(num), color))
    else:
        return "%s=%-4s" % (lead, str(num))


def hostcolor(host, stats, color=True):
    if color:
        if stats['failures'] != 0 or stats['unreachable'] != 0:
            return "%-37s" % ansible_color.stringc(host, 'red')
        elif stats['changed'] != 0:
            return "%-37s" % ansible_color.stringc(host, 'yellow')
        else:
            return "%-37s" % ansible_color.stringc(host, 'green')
    return "%-26s" % host


def execute_ansible(playbook, args):
    hosts = args.inventory or (LOCAL_HOSTS if playbook == PROVISION
                               else HOSTS_FILE)
    playbook += ".yml"
    path_to_playbook = os.path.join(PATH_TO_PLAYBOOKS, playbook)

    # From ansible-playbook:
    stats = ansible.callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=VERBOSITY)
    # if options.step:
    # # execute step by step
    #     playbook_cb.step = options.step
    # if options.start_at:
    # # start execution at a specific task
    #     playbook_cb.start_at = options.start_at
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats,
                                                  verbose=utils.VERBOSITY)

    pb = ansible.playbook.PlayBook(
        # From ansible-playbook:
        playbook=path_to_playbook,
        inventory=ansible.inventory.Inventory(hosts),
        extra_vars=utils.parse_yaml_from_file(args.settings),
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        stats=stats,
    )

    failed_hosts = []
    unreachable_hosts = []

    pb.run()

    hosts = sorted(pb.stats.processed.keys())
    callbacks.display(callbacks.banner("PLAY RECAP"))
    playbook_cb.on_stats(pb.stats)

    for h in hosts:
        t = pb.stats.summarize(h)
        if t['failures'] > 0:
            failed_hosts.append(h)
        if t['unreachable'] > 0:
            unreachable_hosts.append(h)

    retries = failed_hosts + unreachable_hosts

    if len(retries) > 0:
        filename = pb.generate_retry_inventory(retries)
        if filename:
            callbacks.display(
                "           to retry, use: --limit @%s\n" % filename)

    for h in hosts:
        t = pb.stats.summarize(h)

        callbacks.display("%s : %s %s %s %s" % (
            hostcolor(h, t),
            colorize('ok', t['ok'], 'green'),
            colorize('changed', t['changed'], 'yellow'),
            colorize('unreachable', t['unreachable'], 'red'),
            colorize('failed', t['failures'], 'red')),
            screen_only=True
        )

        callbacks.display("%s : %s %s %s %s" % (
            hostcolor(h, t, False),
            colorize('ok', t['ok'], None),
            colorize('changed', t['changed'], None),
            colorize('unreachable', t['unreachable'], None),
            colorize('failed', t['failures'], None)),
            log_only=True
        )

    print ""
    if len(failed_hosts) > 0:
        return 2
    if len(unreachable_hosts) > 0:
        return 3


def main():
    args = parser_init()
    for playbook in (p for p in PLAYBOOKS if getattr(args, p)):
        execute_ansible(playbook, args)

if __name__ == '__main__':
    sys.exit(main())
