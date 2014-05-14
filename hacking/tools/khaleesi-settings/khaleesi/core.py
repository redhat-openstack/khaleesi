#!/usr/bin/env python

"""khaleesi-settings generates settings based on the settings directory.

 Usage:
    khaleesi-settings -h | --help
    khaleesi-settings [options] --config-dir=<PATH> <command> [<args> ...]

 Options:
    --log-level=<log-level>     Log levels: debug, info, warning
                                            error, critical
                                [default: warning]

 Commands:
     help
     generate
"""

from tree import OrderedTree
from docopt import docopt
import docstring
import log_color
import logging
import settings
import sys
import yaml
import yaml_utils


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
    logging.debug("DocString for Generate: %s",  doc_string)

    parsed = docopt(doc_string, options_first=True, argv=args)
    logging.info("Parsed: \n%s", parsed)

    output_file = _extract_value_for_option(parsed, '<output-file>')
    extra_vars = _extract_value_for_option(
        parsed, '--extra-vars', must_exist=False)

    # get all args and convert that to
    # directory: filename
    # provision: rdo
    # rdo/version: icehouse.
    settings_tree = OrderedTree(delimiter='-')
    for k, v in parsed.items():
        if not v:
            continue
        #  delete the leading --
        key = k[2:] + '-' + settings.value_indicator_key
        settings_tree[key] = v
        logging.debug("%s: %s", key, v)

    logging.debug(yaml_utils.to_yaml(
        "Directory structure from args:", settings_tree))

    loader = settings.Loader(config_dir, settings_tree)
    _update_extra_vars(extra_vars, loader)
    all_settings = loader.settings_tree()
    logging.debug("\n" + yaml.safe_dump(
        all_settings, default_flow_style=False))
    logging.info("Writing to file: %s", output_file)
    with open(output_file, 'w') as out:
        out.write(yaml.safe_dump(all_settings))


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


def test_generate(args):
    _setup_logging('DEBUG')
    doc_string = generate.__doc__.format(
        options=docstring.Generator('test/data/settings').generate()
    )
    logging.debug(doc_string)
    logging.info("args: %s" % args)
    parsed = docopt(doc_string, options_first=True)
    logging.info("parsed dict: %s" % parsed)


def _setup_logging(level):
    log_color.enable()
    numeric_val = getattr(logging, level.upper(), None)
    if not isinstance(numeric_val, int):
        raise ValueError("Invalid log level: %s" % level)
    fmt = "%(filename)s:%(lineno)3s| %(funcName)20s() : %(message)s"
    logging.basicConfig(level=numeric_val, format=fmt)


def main(args=sys.argv):
    yaml_utils.register()

    # given a directory tree can you generate docstring?
    args = docopt(__doc__, options_first=True)
    _setup_logging(args['--log-level'])

    cmd = args['<command>']
    config_dir = args['--config-dir']
    if cmd == 'help':
        return usage(config_dir)

    if cmd == 'generate':
        return generate(config_dir, args['<args>'])

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
