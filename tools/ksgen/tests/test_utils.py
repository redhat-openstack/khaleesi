from ksgen import yaml_utils
from os.path import dirname, realpath

TEST_DIR = dirname(realpath(__file__))
yaml_utils.register()


def print_yaml(msg, x):
    import logging
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


