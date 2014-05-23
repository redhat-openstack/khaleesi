"""
Usage:
    python test_tree.py <method_name>
    py.test test_tree.py [options]
"""

from configure import Configuration
import logging
from khaleesi import yaml_utils

yaml_utils.register()


def print_yaml(msg, x):
    logging.info(yaml_utils.to_yaml(msg, x))


def test_merge():
    d1 = {
        "d1": [1, 2, 3],
        "s": "foo",
        "a": [1, 2, 3],
        "nested_dict": {
            "d1": "ok",
            "d": "ok"
        }
    }
    c1 = Configuration.from_dict(d1)
    print_yaml("d1", d1)

    d2 = {
        "d2": "foobar",
        "s": "foobar",
        "a": [3, 4, 5],
        "nested_dict": {
            "d2": "ok",
            "d": {
                "foo": "bar"
            }
        }
    }
    c2 = Configuration.from_dict(d2)
    print_yaml("d2", d2)

    c3 = c1.merge(c2)
    print_yaml("Merged", dict(c3))


def _enable_logging(level=None):
    level = level or "debug"

    from khaleesi import log_color
    log_color.enable()

    numeric_val = getattr(logging, level.upper(), None)
    if not isinstance(numeric_val, int):
        raise ValueError("Invalid log level: %s" % level)
    fmt = "%(filename)15s:%(lineno)3s| %(funcName)20s() : %(message)s"
    logging.basicConfig(level=numeric_val, format=fmt)


def usage():
    help = """
%(usage)s

Methods:
    %(methods)s
""" % {
        "usage": __doc__,
        "methods": '\n    '.join([
            m for m in globals().keys() if m.startswith('test_')
        ])
    }
    print(help)

if __name__ == '__main__':
    import sys
    _enable_logging()
    try:
        fn = sys.argv[1]
    except IndexError:
        fn = 'usage'

    ret = locals()[fn]()
    sys.exit(ret)
