#!/usr/bin/env python
import argparse
import os
import sys


KHALEESI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "..", "..", ".."))
PATH_TO_PLAYBOOKS = os.path.join(KHALEESI_DIR, "playbooks")
assert "playbooks" == os.path.basename(PATH_TO_PLAYBOOKS), \
    "Bad path to playbooks"
VERBOSITY = 0
KSGEN_SETTINGS_YML = "ksgen_settings.yml"


def file_exists(prs, filename):
    if not os.path.exists(filename):
        prs.error("The file %s does not exist!" % filename)
    return filename


def main():
    args = parser.parse_args()
    args.func(args)


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', default=VERBOSITY, action="count",
                    help="verbose mode (-vvv for more,"
                         " -vvvv to enable connection debugging)")
parser.add_argument("--settings",
                    default=KSGEN_SETTINGS_YML,
                    type=lambda x: file_exists(parser, x),
                    help="settings file to use. default: %s"
                         % KSGEN_SETTINGS_YML)
subparsers = parser.add_subparsers(metavar="COMMAND")


if __name__ == '__main__':
    sys.exit(main())
