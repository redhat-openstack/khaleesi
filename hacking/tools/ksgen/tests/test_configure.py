"""
Usage:
    python test_tree.py <method_name>
    py.test test_tree.py [options]
"""

from configure import Configuration, ConfigurationError
from ksgen import yaml_utils
import logging
import pytest
import yaml

yaml_utils.register()


def print_yaml(msg, x):
    logging.info(yaml_utils.to_yaml(msg, x))


def verify_key_val(cfg, source_dict, key):
    """ Assuming cfg is created from source_dict, returns true if
    cfg[key] == source_dict[key]"""

    keys = key.split('.')

    leaf_cfg = cfg
    leaf_dict = source_dict
    for k in keys:
        leaf_cfg = leaf_cfg[k]
        leaf_dict = leaf_dict[k]
    return leaf_cfg == leaf_dict


def test_simple_merge():
    src_dict = {
        "merge": "src merge",
        "src": 'src only',
        'nested_dict': {
            'merge': 'nested src merge',
            'src': 'nested src only'
        }
    }

    other_dict = {
        "merge": "other merge",
        "other": 'other only',
        'nested_dict': {
            'merge': 'nested other merge',
            'other': 'nested other only'
        }
    }


    src = Configuration.from_dict(src_dict)
    print_yaml("Src", src)

    other = Configuration.from_dict(other_dict)
    print_yaml("Other", other)

    merged = src.merge(other)
    print_yaml("merged", merged)

    print_yaml("Src after merge", src)
    print_yaml("Other after merge", other)

    assert verify_key_val(src, src_dict, 'merge')
    assert verify_key_val(src, src_dict, 'src')
    assert verify_key_val(src, src_dict, 'nested_dict.merge')
    assert verify_key_val(src, src_dict, 'nested_dict.src')

    with pytest.raises(KeyError):
        verify_key_val(src, src_dict, 'other')

    assert verify_key_val(merged, other_dict, 'merge')
    assert verify_key_val(merged, src_dict, 'src')
    assert verify_key_val(merged, other_dict, 'other')
    return

def test_array_extend():
    src_dict = {
        "src": [11, 12, 13],
        "merge": [100, 101, 102],
        'nested_dict': {
            'src': [111, 112, 113],
            'merge': [1000, 1001, 1002]
        }
    }

    other_dict = {
        "other": [22, 22, 23],
        "merge": [200, 202, 202],
        'nested_dict': {
            'other': [222, 222, 223],
            'merge': [2000, 2002, 2002]
        }
    }


    src = Configuration.from_dict(src_dict)
    print_yaml("Src", src)

    other = Configuration.from_dict(other_dict)
    print_yaml("Other", other)

    merged = src.merge(other)
    print_yaml("merged", merged)

    print_yaml("Src after merge", src)
    print_yaml("Other after merge", other)

    assert verify_key_val(src, src_dict, 'merge')
    assert verify_key_val(src, src_dict, 'src')
    assert verify_key_val(src, src_dict, 'nested_dict.merge')
    assert verify_key_val(src, src_dict, 'nested_dict.src')

    with pytest.raises(KeyError):
        verify_key_val(src, src_dict, 'other')

    assert verify_key_val(merged, src_dict, 'src')
    assert verify_key_val(merged, other_dict, 'other')
    assert merged['merge'] == src_dict['merge'] + other_dict['merge']
    assert verify_key_val(merged, src_dict, 'nested_dict.src')
    assert verify_key_val(merged, other_dict, 'nested_dict.other')


def test_overwrite_tag():
    src_yaml = """
    foo: bar
    """

    overwrite_fail_yaml = """
    foo: [1, 2, 3]
    """
    src = Configuration.from_string(src_yaml)
    print_yaml("Src", src)

    overwrite_fail = Configuration.from_string(overwrite_fail_yaml)
    print_yaml("Overwrite fail", overwrite_fail)

    error_raised = True
    with pytest.raises(ConfigurationError):
        merge = src.merge(overwrite_fail)
        error_raised = False
    assert error_raised
    logging.debug("Raised ConfigurationError")
    assert src.foo == 'bar'

    # ### use overwrite to overwrite src.foo
    overwrite_yaml = """
    foo: !overwrite [1, 2, 3]
    """
    overwrite = Configuration.from_string(overwrite_yaml)
    print_yaml("Overwrite", overwrite)
    merge = src.merge(overwrite)
    print_yaml("Merged", merge)



def test_monkey_patch_merge():
    """
        Monkey patch configure so that merge will
        append lists instead of replacing them
    """
    src_dict = {
        "d1": [1, 2, 3],
        "s": "foo",
        "a": [1, 2, 3],
        "nested_dict": {
            "d1": "ok",
            "d": "ok"
        }
    }
    src = Configuration.from_dict(src_dict)
    print_yaml("Src", src)

    other_dict = {
        "d2": [1, 3, 5],
        "s": "bar",
        "a": [3, 2, 8],
        "nested_dict": {
            "d1": "ok",
            "d": "ok"
        }
    }
    src = Configuration.from_dict(src_dict)
    print_yaml("Merged", src)

    other = Configuration.from_dict(other_dict)
    merged = src.merge(other)
    print_yaml("src", merged)
    print_yaml("Merged", src)
    assert merged['d1'] == [1, 2, 3]
    assert merged['d2'] == [1, 3, 5]
    assert merged['a'] == [1, 2, 3, 3, 2, 8]
    assert merged['s'] == 'bar'
    return
    src = Configuration.from_string("""array: [1, 2, 3] """)
    print_yaml("Original config", src)

    other = Configuration.from_string("""array: [2, 3, 8, 9] """)
    merged = src.merge(other)
    print_yaml("Merged", merged)
    assert merged['array'] == [1, 2, 3, 2, 3, 8, 9]

    # ### test overwrite

    overwrite = Configuration.from_string(""" array: !overwrite [0, 0, 0] """)
    print_yaml("Overwrite", overwrite)

    merged = src.merge(overwrite)
    print_yaml('Merge with overwrite', merged)

    assert merged['array'] == [0, 0, 0]

    another_overwrite = Configuration.from_string(""" array: !overwrite [1, 1, 1] """)
    print_yaml("Another Overwrite", another_overwrite)

    merged = merged.merge(another_overwrite)
    print_yaml('Merge with another overwrite', merged)

    assert merged['array'] == [1, 1, 1]
    # extend overwritten
    print_yaml("Extending src", src)

    merged = merged.merge(src)
    print_yaml('Merge with src', merged)

    assert merged['array'] == [1, 1, 1, 1, 2, 3]


    from ksgen.tree import OrderedTree
    tree = OrderedTree(delimiter='.')
    tree.update(merged)
    print_yaml("Merged", tree)


def test_ref():
    src_string = """
    foo: bar
    ref_foo: !ref:foo
    """

    src = Configuration.from_string(src_string)
    print_yaml("yaml for src", src)
    assert src.ref_foo == src.foo

    missing_ref_string = """
    foo: bar
    ref_foo: !ref:bar
    """

    raised_key_error = True
    with pytest.raises(KeyError):
        missing_ref = Configuration.from_string(missing_ref_string)
        raised_key_error = False
    assert raised_key_error
    logging.debug("Raised KeyError")


def test_custom_lists():

    class OverwriteList(list):
        def __init__(self, values):
            super(OverwriteList, self).__init__(values)
            self.values = values

        def merge(self, other):
            logging.debug(".....................")
            super(OverwriteList, self).append(other)

    logging.debug(yaml.dump(OverwriteList([1, 2, 3])))

    def overwrite_list_representer(dumper, data):
        return dumper.represent_sequence(u'!overwrite_list', data)

    yaml.SafeDumper.add_representer(OverwriteList, overwrite_list_representer)
    logging.debug(yaml.dump(OverwriteList([1, 2, 3])))

    def overwrite_list_constructor(loader, node):
        values = loader.construct_sequence(node)
        print(values)
        return OverwriteList(values)

    yaml.add_constructor(u'!overwrite_list', overwrite_list_constructor)

    src = Configuration.from_string("""
foo: [1, 2, 3]
bar: !overwrite_list
- 11
- 12
- 19

""")

    print_yaml("Original config", src)

    other = Configuration.from_string("""
foo: [2, 3, 8, 9]
bar: !overwrite_list
- 25
- 27
- 29

""")
    merged = src.merge(other)
    print_yaml("Merged", merged)

    class AppendList(list, yaml.YAMLObject):
        yaml_tag = u'!append_list'

        def __init__(self, values):
            super(AppendList, self).__init__(values)

        @classmethod
        def from_yaml(cls, loader, node):
            return AppendList(loader.construct_sequence(node))

        @classmethod
        def to_yaml(cls, dumper, data):
            return dumper.represent_sequence(cls.yaml_tag, data)

    logging.debug(
        yaml.dump({
            'foo': AppendList([1, 2, 3])
        })
    )

    append_list = yaml.load("""
foo: !append_list [1, 2, 3]
""")
    logging.debug(append_list)
    assert isinstance(append_list['foo'], AppendList)


def test_merge_error():
    src_dict = {
        "d1": [1, 2, 3],
        "s": "foo",
        "a": [1, 2, 3],
        "nested_dict": {
            "d1": "ok",
            "d": "ok"
        }
    }

    other_dict = {
        "d2": "foobar",
        "s": "foobar",
        "a": [3, 4, 5],
        "nested_dict": {
            "d2": "ok",
            "d": {            # ### raises ConfigError
                "foo": "bar"
            }
        }
    }
    src = Configuration.from_dict(src_dict)
    print_yaml("src", src)

    other = Configuration.from_dict(other_dict)
    print_yaml("other", other)

    with pytest.raises(ConfigurationError):
        merged = src.merge(other)
        print_yaml("Merged", dict(merged))
    logging.info("Merge raised configuration error")


def _enable_logging(level=None):
    level = level or "debug"

    from ksgen import log_color
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
