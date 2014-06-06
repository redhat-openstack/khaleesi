from configure import Configuration, ConfigurationError
from ksgen import docstring, yaml_utils, utils
from ksgen.tree import OrderedTree
from ksgen.yaml_utils import LookupDirective
from docopt import docopt
import logging
import os
import yaml


VALUES_KEY = '!value'
logger = logging.getLogger(__name__)


class KeyValueError(Exception):
    def __init__(self, arg, reason, *args, **kwargs):
        super(KeyValueError, self).__init__(*args, **kwargs)
        self.arg = arg
        self.reason = reason

    def __str__(self):
        return "Invalid key-value pair: %s, - %s" % (self.arg, self.reason)


class OptionError(Exception):
    def __init__(self, paths, *args, **kwargs):
        super(OptionError, self).__init__(*args, **kwargs)
        self._paths = paths

    def __str__(self):
        return "Invalid values passed, files : %s not found" % self._paths


class Generator(object):
    """
Usage:
    generate [options] <output-file>
    generate [--extra-vars=KEY_PAIR]... [options] <output-file>

Options:
    --rule=<file>...       Rules file that contains generation rules
                            Process the rules first, so the additional
                            args will override args in rules file
    --extra-vars=<val>...   Provide extra vars {options}
    """

    def __init__(self, config_dir, args):
        self.config_dir = config_dir
        self.args = args
        logger.debug("config_dir: %s, args: %s", config_dir, args)
        self._doc_string = Generator.__doc__.format(
            options=docstring.Generator(config_dir).generate()
        )
        self.settings = None
        self.output_file = None
        self.rules_file = None
        self._extra_vars = None

    def run(self):
        self._parse()
        # return
        loader = Loader(self.config_dir, self.settings)
        self._merge_extra_vars(loader)
        all_settings = loader.settings()

        logger.debug(yaml_utils.to_yaml("All Settings", all_settings))
        logger.info("Writing to file: %s", self.output_file)
        with open(self.output_file, 'w') as out:
            out.write(yaml.safe_dump(all_settings, default_flow_style=False))

    def _parse(self):
        logger.debug("Parsing: %s", self.args)
        logger.debug("DocString for Generate: %s", self._doc_string)

        parsed = docopt(self._doc_string, options_first=True, argv=self.args)
        logger.info("Parsed: \n%s", parsed)

        self.output_file = utils.extract_value(
            parsed, '<output-file>', optional=False)
        self.rules_file = utils.extract_value(parsed, '--rule')
        self._extra_vars = utils.extract_value(parsed, '--extra-vars')
        self._validate_rules()

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

        # filter only options; [ --foo, fooz, --bar baz ] -> [--foo, --bar]
        options = [x for x in self.args if x.startswith('--')]

        settings = OrderedTree(delimiter='-')
        for option in options:   # iterate options to preserve order of args
            option = option.split('=')[0]
            value = parsed.get(option)
            if not value:
                continue

            key = option[2:] + settings.delimiter + VALUES_KEY
            settings[key] = value
            logger.debug("%s: %s", key, value)

        logger.debug(yaml_utils.to_yaml(
            "Directory structure from args:", settings))
        self.settings = settings

    def _validate_rules(self):
        pass

    def _merge_extra_vars(self, loader):
        if not self._extra_vars or len(self._extra_vars) == 0:
            return

        for var in self._extra_vars:
            if var.startswith('@'):
                loader.load_file(var[1:])  # remove @
            elif '=' in var:
                key, val = var.split('=', 1)
                tree = OrderedTree(delimiter='.')
                tree[key] = val
                loader.merge(tree)
            else:
                raise KeyValueError(var, "No = found between key and value")


class Loader(object):
    def __init__(self, config_dir, settings):
        self._settings = settings
        self._config_dir = config_dir
        self._loaded = False
        self._all_settings = None
        self._file_list = None
        self._invalid_paths = None

    def settings(self):
        self._load()
        LookupDirective.lookup_table = self._all_settings
        return self._all_settings

    def load_file(self, f):
        self._load()
        try:
            cfg = Configuration.from_file(f).configure()
        except ConfigurationError as e:
            logger.error("Error loading: %s; reason: %s", f, e)
            raise
        self._all_settings.merge(cfg)

    def merge(self, tree):
        self._load()
        self._all_settings.merge(tree)

    def _load(self):
        if self._loaded:
            return

        self._all_settings = OrderedTree('!')
        self._file_list = []
        self._invalid_paths = []
        self._create_file_list(self._settings, self._file_list)

        logger.info(
            "\nList of files to load :\n  - %s",
            '\n  - '.join([
                x[len(self._config_dir) + 1:] for x in self._file_list
            ]))

        if self._invalid_paths:
            logger.info("invalid files :\n %s", '\n'.join(self._invalid_paths))
            raise OptionError(self._invalid_paths)

        all_cfg = Configuration.from_dict({})
        for f in self._file_list:
            logger.debug('Loading file: %s', f)
            try:
                cfg = Configuration.from_file(f).configure()
            except ConfigurationError as e:
                logger.error("Error loading: %s; reason: %s", f, e)
                raise
            all_cfg.merge(cfg)
        self._all_settings.merge(all_cfg)
        self._loaded = True

    def _create_file_list(self, settings, file_list, parent_path=""):
        """ Appends list of files to be process to self._file_list
            and list of invalid file paths to self._invalid_paths
        """
        logger.debug('settings:\n %s \n parent: %s \n files: %s',
                     settings, parent_path, file_list)

        for key, sub_tree in settings.items():
            # ignore the special key value
            if key == VALUES_KEY:
                continue

            logger.debug("key: %s, subtree: %s", key, sub_tree)
            path = "%(parent_path)s%(key)s%(sep)s%(file)s" % {
                'parent_path': parent_path,
                'key': key,
                'sep': os.sep,
                'file': sub_tree[VALUES_KEY]
            }

            abs_file_path = os.path.abspath(
                self._config_dir + os.sep + path + '.yml')
            file_list.append(abs_file_path)
            logger.debug('path: %s', abs_file_path)

            if not os.path.exists(abs_file_path):
                self._invalid_paths.append(abs_file_path)

            # recurse if there are sub settings
            if (isinstance(sub_tree, dict)
                    and len(sub_tree.keys()) > 1):
                logger.debug('recursing into: sub-tree: %s', sub_tree)
                self._create_file_list(sub_tree, file_list, path + os.sep)
