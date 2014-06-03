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

from configure import Configuration, ConfigurationError
import logging
import yaml


def to_yaml(header, x):
    """formats x to yaml and adds header on top"""

    return """
%(header)s
----------------------
%(yml)s
----------------------
    """ % {
        "header": header,
        "yml": yaml.safe_dump(x, default_flow_style=False)
    }


@Configuration.add_constructor('join')
def _join_constructor(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])


class LookupDirective(yaml.YAMLObject):
    lookup_table = None
    yaml_tag = u'!lookup'
    yaml_dumper = yaml.SafeDumper

    def __init__(self, key):
        self._key = key

    def lookup(self):
        if not LookupDirective.lookup_table:
            return '{{ %s }}' % self._key
        if self._key not in LookupDirective.lookup_table:
            return '{{ %s }}' % self._key
        return LookupDirective.lookup_table[self._key]


    def __repr__(self):
        return "%(class)s(%(lookup)s)" % {
            'class': self.__class__.__name__,
            'lookup': self._key
        }

    @classmethod
    def from_yaml(cls, loader, node):
        return LookupDirective(loader.construct_scalar(node))

    @classmethod
    def to_yaml(cls, dumper, node):
        value = node.lookup()
        return dumper.represent_data(value)


class OverwriteDirective(yaml.YAMLObject):
    yaml_tag = u'!overwrite'
    yaml_dumper = yaml.SafeDumper

    def __init__(self, value):
        self.value = value

    @classmethod
    def from_yaml(cls, loader, node):
        return OverwriteDirective(loader.construct_sequence(node))

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_sequence(cls.yaml_tag, data.value)


def patch_configure_getattr(self, name):
    if name.startswith('__'):
        raise AttributeError(name)
    return self[name]
Configuration.__getattr__ = patch_configure_getattr


def patch_configure_merge(self, config):
    from copy import deepcopy
    from collections import Mapping, Sequence
    for k, v in config.items():
        if k not in self:
            self[k] = deepcopy(v)
            continue

        if isinstance(v, OverwriteDirective):
            self[k] = deepcopy(v.value)
            continue

        if type(self[k]) != type(v):
            raise ConfigurationError(
                "cannot merge type '%s' with type '%s' for key '%s'" % (
                    self[k].__class__.__name__,
                    v.__class__.__name__,
                    k
                ))

        if isinstance(v, Mapping):
            patch_configure_merge(self[k], v)
            continue

        if isinstance(v, Sequence) and not hasattr(self[k], 'extend'):
            self[k] = deepcopy(v)
        else:
            self[k].extend(v)



Configuration._merge = patch_configure_merge


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
    from ksgen.tree import OrderedTree

    yaml.SafeDumper.add_representer(
        OrderedTree,
        lambda dumper, value: represent_odict(
            dumper, u'tag:yaml.org,2002:map', value)
    )
    yaml.SafeDumper.add_representer(
        Configuration,
        lambda dumper, value: represent_odict(
            dumper, u'tag:yaml.org,2002:map', value)
    )
    yaml.SafeDumper.add_representer(
        OrderedDict,
        lambda dumper, value: represent_odict(
            dumper, u'tag:yaml.org,2002:map', value)
    )
