from os import path
import ansible.playbook
from ansible import callbacks
import ansible.color
import ansible.inventory
import ansible.utils

from kcli import core


HOSTS_FILE = "hosts"
LOCAL_HOSTS = "local_hosts"
PROVISION = "provision"
PLAYBOOKS = [PROVISION, "install", "test", "collect-logs", "cleanup"]


# ansible-playbook
# https://github.com/ansible/ansible/blob/devel/bin/ansible-playbook

# From ansible-playbook
def colorize(lead, num, color):
    """ Print 'lead' = 'num' in 'color' """
    if num != 0 and color is not None:
        return "%s%s%-15s" % (ansible.color.stringc(lead, color),
                              ansible.color.stringc("=", color),
                              ansible.color.stringc(str(num), color))
    else:
        return "%s=%-4s" % (lead, str(num))


def hostcolor(host, stats, color=True):
    if color:
        if stats['failures'] != 0 or stats['unreachable'] != 0:
            return "%-37s" % ansible.color.stringc(host, 'red')
        elif stats['changed'] != 0:
            return "%-37s" % ansible.color.stringc(host, 'yellow')
        else:
            return "%-37s" % ansible.color.stringc(host, 'green')
    return "%-26s" % host


def execute_ansible(playbook, args):
    ansible.utils.VERBOSITY = args.verbose
    hosts = args.inventory or (LOCAL_HOSTS if playbook == PROVISION
                               else HOSTS_FILE)
    playbook = playbook.replace("-", "_") + ".yml"
    path_to_playbook = path.join(core.PATH_TO_PLAYBOOKS, playbook)

    # From ansible-playbook:
    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=ansible.utils.VERBOSITY)
    # if options.step:
    # # execute step by step
    #     playbook_cb.step = options.step
    # if options.start_at:
    # # start execution at a specific task
    #     playbook_cb.start_at = options.start_at
    runner_cb = callbacks.PlaybookRunnerCallbacks(
        stats,
        verbose=ansible.utils.VERBOSITY
    )

    pb = ansible.playbook.PlayBook(
        # From ansible-playbook:
        playbook=path_to_playbook,
        inventory=ansible.inventory.Inventory(hosts),
        extra_vars=ansible.utils.parse_yaml_from_file(args.settings),
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        stats=stats,
    )

    failed_hosts = []
    unreachable_hosts = []

    if args.verbose:
        ansible_cmd = ["ansible-playbook"]
        ansible_cmd.append("-" + "v" * args.verbose)
        ansible_cmd.append("-i " + hosts)
        ansible_cmd.append("--extra-vars @" + args.settings)
        ansible_cmd.append(path_to_playbook)
        print "ANSIBLE COMMAND: " + " ".join(ansible_cmd)

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
        raise Exception(2)
    if len(unreachable_hosts) > 0:
        raise Exception(3)


def ansible_wrapper(args):
    """Wraps the 'anisble-playbook' CLI."""
    playbooks = [p for p in PLAYBOOKS if getattr(args, p, False)]
    if not playbooks:
        core.parser.error("No playbook to execute (%s)" % PLAYBOOKS)

    for playbook in (p for p in PLAYBOOKS if getattr(args, p, False)):
        print "Executing Playbook: %s" % playbook
        try:
            execute_ansible(playbook, args)
        except Exception:
            raise Exception("Playbook %s failed!" % playbook)


execute_parser = core.subparsers.add_parser('execute',
                                            help="execute playbooks")
execute_parser.add_argument('-i', '--inventory',
                            default=None,
                            type=lambda x: core.file_exists(execute_parser, x),
                            help="Inventory file to use. "
                                 "Default: {lcl}. "
                                 "NOTE: to reuse old environment use {"
                                 "host}".
                            format(lcl=LOCAL_HOSTS, host=HOSTS_FILE))
execute_parser.add_argument("--provision", action="store_true",
                            help="provision fresh nodes from server")
execute_parser.add_argument("--install", action="store_true",
                            help="install Openstack on nodes")
execute_parser.add_argument("--test", action="store_true",
                            help="execute tests")
execute_parser.add_argument("--collect-logs", action="store_true",
                            help="Pull logs from nodes")
execute_parser.add_argument("--cleanup", action="store_true",
                            help="cleanup nodes")
execute_parser.set_defaults(func=ansible_wrapper)
