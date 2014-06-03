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
"""

from __future__ import print_function
from ksgen import docstring, log_color, settings, yaml_utils
from ksgen.tree import OrderedTree
from docopt import docopt
import logging
import sys
import yaml


class KeyValueError(Exception):
    def __init__(self, arg, reason, *args, **kwargs):
        super(KeyValueError, self).__init__(*args, **kwargs)
        self.arg = arg
        self.reason = reason

    def __str__(self):
        return "Invalid key-value pair: %s, - %s" % (self.arg, self.reason)


def generate(config_dir, args):
    """
Usage:
    generate [options] <output-file>
    generate [--extra-vars=KEY_PAIR]... [options] <output-file>

Options:
    --extra-vars=<val>...   Provide extra vars {options}
    """

    logging.debug("config_dir: %s, args: %s", config_dir, args)
    doc_string = generate.__doc__.format(
        options=docstring.Generator(config_dir).generate()
    )
    logging.debug("Parsing: %s", args)
    logging.debug("DocString for Generate: %s", doc_string)

    parsed = docopt(doc_string, options_first=True, argv=args)
    logging.info("Parsed: \n%s", parsed)

    output_file = _extract_value_for_option(parsed, '<output-file>')
    extra_vars = _extract_value_for_option(
        parsed, '--extra-vars', must_exist=False)

    # create the settings tree and preserve the order in which arguments
    # are passed.  Convert all args into an ordered tree so that
    # --foo fooz  --too moo --foo-bar baaz  --foo-arg vali
    # will be like the ordered tree below
    # foo:
    #   <special-key>: fooz
    #   bar:       ###  <-- foo-bar is not foo/bar
    #     <special-key>: baaz
    #   arg:       ###  <-- arg comes after bar
    #     <special-key>: val
    # too:
    #   <special-key>: moo

    settings_tree = OrderedTree(delimiter='-')
    # filter only options; [ --foo, fooz, --bar baz ] -> [--foo, --bar]
    options = [x for x in args if x.startswith('--')]

    for option in options:   # iterate options to preserve order of args
        option = option.split('=')[0]
        value = parsed.get(option)
        if not value:
            continue

        key = option[2:] + '-' + settings.VALUES_KEY
        settings_tree[key] = value
        logging.debug("%s: %s", key, value)

    logging.debug(yaml_utils.to_yaml(
        "Directory structure from args:", settings_tree))
    loader = settings.Loader(config_dir, settings_tree)
    _update_extra_vars(extra_vars, loader)
    all_settings = loader.settings_tree()
    logging.debug("\n" + yaml.safe_dump(
        all_settings, default_flow_style=False))
    logging.info("Writing to file: %s", output_file)
    with open(output_file, 'w') as out:
        out.write(yaml.safe_dump(all_settings, default_flow_style=False))


def _extract_value_for_option(mapping, key, default=None, must_exist=True):

    # raise KeyError if it doesn't exist
    val = mapping[key] if must_exist else None

    if key not in mapping:
        return default

    val = val or mapping[key]    # reuse val already set
    del mapping[key]
    return val


def _update_extra_vars(extra_vars, loader):
    if not extra_vars or len(extra_vars) == 0:
        return

    for var in extra_vars:
        if var.startswith('@'):
            loader.load_file(var[1:])
        elif '=' in var:
            key, val = var.split('=', 1)
            tree = OrderedTree(delimiter='.')
            tree[key] = val
            loader.update(tree)
        else:
            raise KeyValueError(var, "No = found between key and value")


def usage(path):
    doc_string = "{docs} \n Valid configs are: {config}".format(
        docs=__doc__,
        config=docstring.Generator(path).generate())
    print(doc_string)


def _setup_logging(level):
    log_color.enable()
    numeric_val = getattr(logging, level.upper(), None)
    if not isinstance(numeric_val, int):
        raise ValueError("Invalid log level: %s" % level)
    fmt = "%(filename)s:%(lineno)3s| %(funcName)20s() : %(message)s"
    logging.basicConfig(level=numeric_val, format=fmt)


def main(args=None):
    args = args or sys.argv
    yaml_utils.register()

    # given a directory tree can you generate docstring?
    args = docopt(__doc__, options_first=True)
    _setup_logging(args['--log-level'])

    cmd = args['<command>']
    from os.path import abspath
    config_dir = abspath(args['--config-dir'])
    if cmd == 'help':
        return usage(config_dir)

    if cmd == 'generate':
        return generate(config_dir, args['<args>'])

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
