#!/bin/env python

import argparse
import os


'''
Usage:

Go to jenkins and copy and paste the kahleesi based job name that you want to
run, for example:

khaleesi-rdo-juno-production-fedora-20-aio-packstack-neutron-gre-rabbitmq-
tempest-rpm-minimal

All Khaleesi jobs have the following format:

khaleesi-{product}-{product-version}-{product-version-repo}-{distro}-{topology}
-{installer}-{network}-{network-variant}-{messaging}-{tester}-{tester-setup}
-{tester-tests}

So, just run the easydeploy:

easydeploy.py khaleesi-rdo-juno-production-fedora-20-aio-packstack-neutron-gre
-rabbitmq-tempest-rpm-minimal ksgen_settings.yml

Options and default values:
--provisioner = packstack
--workarounds = enabled
--provisioner-site = qeos
--provisioner-site-user = rhos-jenkins

Feel free to change it.

Other values that you can override you can check with --help option
'''

product = ['rhos', 'rdo']
product_version = ['5.0', 'icehouse', '4.0', 'juno', 'upstream', 'havana']
product_version_repo = ['delorean', 'production', 'puddle', 'poodle', 'stage']
distro = ['centos-7.0', 'rhel-7.0', 'fedora-20', 'rhel-6.5', 'centos-6.5']
topology = ['default', 'vagrant', 'aio_two_nic', 'baremetal', 'aio',
            'nodes_virt', 'multinode', 'nodes', 'ha']
installer = ['packstack', 'staypuft', 'foreman', 'instack', 'opm']
network = ['neutron', 'nova']
network_variant = ['flatdhcp', 'gre', 'ml2-vxlan', 'ml2-gre']
messaging = ['qpidd', 'rabbitmq']
tester = ['unittest', 'tempest']
tester_setup = ['source', 'packstack_provision', 'rpm']
tester_tests = ['none', 'sahara_basic', 'smoke', 'minimal', 'all']

all_in_one = {'product': product, 'product-version': product_version,
              'product-version-repo': product_version_repo, 'distro': distro,
              'topology': topology, 'installer': installer,
              'installer-network': network,
              'installer-network-variant': network_variant,
              'installer-messaging': messaging, 'tester': tester,
              'tester-setup': tester_setup, 'tester-tests': tester_tests}

all_in_one_keys = ['product', 'product-version', 'product-version-repo',
                   'distro', 'topology', 'installer', 'installer-network',
                   'installer-network-variant', 'installer-messaging',
                   'tester', 'tester-setup', 'tester-tests']


def get_all_settings(job_name):
    splited_job_name = job_name.split('-')
    count = 1
    return_value = {}

    try:
        for key in all_in_one_keys:
            default_value = ''
            for _value in all_in_one[key]:
                default_value = splited_job_name[count]
                for x in range(1, _value.count('-')+1):
                    default_value = default_value + '-' + \
                        splited_job_name[count + x]

                if _value == default_value:
                        count += default_value.count('-')+1 if \
                            default_value.count('-') is not 0 else 1
                        return_value[key] = default_value
                        break
    except IndexError:
        return_value = None

    return return_value


def parse_arguments():
    parse = argparse.ArgumentParser(description='Easy deploy script')

    for _value in all_in_one_keys:
        parse.add_argument('--' + _value, dest=_value,
                           help='Override --' + _value)

    parse.add_argument('--config-base', help='Khaleesi settings dir')
    parse.add_argument('--provisioner', default='openstack',
                       help='Set provisioner type')
    parse.add_argument('--workarounds', default='enabled',
                       help='Enable workarounds')
    parse.add_argument('--provisioner-site', default='qeos',
                       help='Set provisioner site')
    parse.add_argument('--provisioner-site-user', default='rhos-jenkins',
                       help='Set openstack user')
    parse.add_argument('--playbook', help='Return the playbook to be used',
                       action='store_true')
    parse.add_argument('--hostfile', help='Specify a host file')
    parse.add_argument('jobname', help='Job name')
    parse.add_argument('ymlfile', help='yml file to be generated')

    return parse.parse_args()


def _normalize_args(options, args, config_dir):

    return_value = '--config-dir=' + config_dir + \
                   '/settings generate --rules-file=' + config_dir + \
                   '/rules/' + options['installer'] + '-' + options['product'] \
                   + '-' + options['topology'] + '.yml'
    return_value += ' --product-version-workaround=' + options['distro']
    return_value += ' --workarounds=' + args.workarounds
    return_value += ' --provisioner=' + args.provisioner
    return_value += ' --provisioner-site=' + args.provisioner_site
    return_value += ' --provisioner-site-user=' + args.provisioner_site_user

    for _value in all_in_one_keys:
        if _value in ['topology', 'product', 'tester', 'tester-setup',
                      'installer', 'job', 'installer-topology']:
            continue
        return_value = return_value + ' --' + _value + '=' + options[_value]

    return_value = return_value + ' ' + args.ymlfile

    return return_value


def override_options(options, args):
    for _value in all_in_one_keys:
        if getattr(args, _value):
            options[_value] = getattr(args, _value)


def main():
    args = parse_arguments()
    options = get_all_settings(args.jobname)

    if options is None:
        print ""
        return -1

    if args.playbook:
        if args.hostfile:
            print "-i %s playbooks/%s.yml" % (args.hostfile, options['installer'])
        else:
            print "playbooks/%s.yml" % options['installer']

    else:
        config_dir = args.config_base or os.getenv('CONFIG_BASE')

        if config_dir:
            arguments = override_options(options, args)
            print _normalize_args(options, args, config_dir)
            return 0
        else:
            print 'Set CONFIG_BASE variable or use --config-base option'
            return -1

if __name__ == "__main__":
    main()
