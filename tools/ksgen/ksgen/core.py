#!/usr/bin/env python

"""ksgen generates settings based on the settings directory.

Usage:
   ksgen -h | --help
   ksgen [options] --config-dir=<PATH> <command> [<args> ...]

Options:
   --log-level=<log-level>     Log levels: debug, info, warning
                                           error, critical
                               [default: warning]

Commands:
    help
    generate

Valid options based on '{path}' are:
{options}
"""

from __future__ import print_function
from ksgen import docstring, log_color, settings, yaml_utils
from docopt import docopt
from os.path import abspath, relpath
import logging
import sys


def usage(path):
    doc_string = __doc__.format(
        path=relpath(path),
        options=docstring.Generator(path).options())
    print(doc_string)


def _setup_logging(level):
    log_color.enable()
    numeric_val = getattr(logging, level.upper(), None)
    if not isinstance(numeric_val, int):
        raise ValueError("Invalid log level: %s" % level)
    fmt = ("%(filename)s:%(lineno)3s| "
           "%(funcName)20s() |%(levelname)8s: %(message)s")
    logging.basicConfig(level=numeric_val, format=fmt)


def main(args=None):
    args = args or sys.argv
    yaml_utils.register()

    # given a directory tree can you generate docstring?
    args = docopt(__doc__, options_first=True)
    _setup_logging(args['--log-level'])

    cmd = args['<command>']
    config_dir = abspath(args['--config-dir'])
    if cmd == 'help':
        return usage(config_dir)

    if cmd == 'generate':
        return settings.Generator(config_dir, args['<args>']).run()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
