# Taken from: https://gist.github.com/miracle2k/3184458
# Credits: Michael Elsdorfer
#
# usage:
# yaml.safe_dump(data, default_flow_style=False)

"""Make PyYAML output an OrderedDict.

It will do so fine if you use yaml.dump(), but that generates ugly,
non-standard YAML code.

To use yaml.safe_dump(), you need the following.
"""

import yaml


def to_yaml(header, x):
    return """
%(header)s
----------------------
%(yml)s
----------------------
""" % {
        "header": header,
        "yml": yaml.safe_dump(x, default_flow_style=False)
    }


def represent_odict(dump, tag, mapping, flow_style=None):
    """Like BaseRepresenter.represent_mapping, but does not issue the sort().
    """
    value = []
    node = yaml.MappingNode(tag, value, flow_style=flow_style)
    if dump.alias_key is not None:
        dump.represented_objects[dump.alias_key] = node
    best_style = True
    if hasattr(mapping, 'items'):
        mapping = mapping.items()
    for item_key, item_value in mapping:
        node_key = dump.represent_data(item_key)
        node_value = dump.represent_data(item_value)
        if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
            best_style = False
        if not (isinstance(node_value, yaml.ScalarNode)
                and not node_value.style):
            best_style = False
        value.append((node_key, node_value))
    if flow_style is None:
        if dump.default_flow_style is not None:
            node.flow_style = dump.default_flow_style
        else:
            node.flow_style = best_style
    return node


def register():
    from collections import OrderedDict
    from configure import Configuration
    from tree import OrderedTree

    yaml.SafeDumper.add_representer(
        OrderedTree,
        lambda dumper, value:
            represent_odict(dumper, u'tag:yaml.org,2002:map', value)
    )
    yaml.SafeDumper.add_representer(
        Configuration,
        lambda dumper, value:
            represent_odict(dumper, u'tag:yaml.org,2002:map', value)
    )
    yaml.SafeDumper.add_representer(
        OrderedDict,
        lambda dumper, value:
            represent_odict(dumper, u'tag:yaml.org,2002:map', value)
    )

