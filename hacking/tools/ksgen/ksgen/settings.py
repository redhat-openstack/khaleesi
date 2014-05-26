from configure import Configuration
from ksgen.tree import OrderedTree
import logging
import os


VALUES_KEY = '!value'


class OptionError(Exception):
    def __init__(self, paths, *args, **kwargs):
        super(OptionError, self).__init__(*args, **kwargs)
        self._paths = paths

    def __str__(self):
        return "Invalid values passed, files : %s not found" % self._paths


class Loader(object):
    def __init__(self, config_dir, settings):
        self._settings = settings
        self._config_dir = config_dir
        self._loaded = False
        self._all_settings = None
        self._file_list = None
        self._invalid_paths = None

    def settings_tree(self):
        self._load()
        return self._all_settings

    def load_file(self, f):
        self._load()
        self._load_file(f)

    def update(self, tree):
        self._load()
        self._all_settings.update(tree)

    def _load(self):
        if self._loaded:
            return

        self._all_settings = OrderedTree('/')
        self._file_list = []
        self._invalid_paths = []
        self._create_file_list(self._settings, "", self._file_list)
        logging.info("files to load :\n %s", '\n'.join(self._file_list))
        logging.info("invalid files :\n %s", '\n'.join(self._invalid_paths))
        if self._invalid_paths:
            raise OptionError(self._invalid_paths)

        for f in self._file_list:
            self._load_file(f)

        self._loaded = True

    def _load_file(self, f):
        logging.debug('Loading file: %s', f)
        cfg = Configuration.from_file(f).configure()
        self._all_settings.update(cfg)

    def _create_file_list(self, settings, parent_path, file_list):
        """ Appends list of files to be process to self._file_list
            and list of invalid file paths to self._invalid_paths
        """
        logging.debug('settings:\n %s \n parent: %s \n files: %s',
                      settings, parent_path, file_list)

        for key, sub_tree in settings.items():
            # ignore the special key value
            if key == VALUES_KEY:
                continue

            logging.debug("key: %s, subtree: %s", key, sub_tree)
            path = "%(parent_path)s%(key)s%(sep)s%(file)s" % {
                'parent_path': parent_path,
                'key': key,
                'sep': os.sep,
                'file': sub_tree[VALUES_KEY]
            }

            abs_file_path = os.path.abspath(self._config_dir + os.sep
                                            + path + '.yml')
            file_list.append(abs_file_path)
            logging.debug('path: %s', abs_file_path)

            if not os.path.exists(abs_file_path):
                self._invalid_paths.append(abs_file_path)

            # recurse if there are sub settings
            if (isinstance(sub_tree, dict)
                    and len(sub_tree.keys()) > 1):
                logging.debug('recursing into: sub-tree: %s', sub_tree)
                self._create_file_list(sub_tree, path + os.sep, file_list)
