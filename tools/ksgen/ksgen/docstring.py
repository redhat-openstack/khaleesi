"""
Generates options list based on the directory structure so that it
can be used with docstring
"""

from ksgen.tree import OrderedTree
import logging
import os


logger = logging.getLogger(__name__)

VALUES = ".values"
MULTIPLE_ALLOWED = ".multiple_allowed"


class Generator(object):
    def __init__(self, config_path, **kwargs):
        self._config_dir = os.path.abspath(config_path)
        self._kwargs = kwargs
        self._parse_tree = None

    def parse_tree(self):
        self._parse_tree = OrderedTree()
        if not os.path.isdir(self._config_dir):
            logger.error("Error: config dir %s does not exist",
                         self._config_dir)
            raise OSError("No such directory: %s", self._config_dir)

        for dir_path, subdirs, files in os.walk(self._config_dir):
            logger.debug("Walking dir: %s", dir_path)
            if dir_path == self._config_dir:
                logger.debug("  ... skipping root dirs")
                continue

            yml_files = {
                os.path.splitext(x)[0] for x in files
                if x.endswith('.yml')}
            logger.debug("  files: %s", yml_files)

            # don't process dirs without yml files
            # but traverse deeper if it is a data dir
            if len(yml_files) == 0:
                if not self._is_data_dir(dir_path):
                    logger.warning(
                        "... skipping dir: [%s]: empty dir "
                        " and not data dir", dir_path)
                    subdirs[:] = []
                else:
                    logger.debug("... skipping: data_dir: %s", dir_path)
                continue

            # add the dir as an option
            self._add_option(dir_path, yml_files)

            logger.debug("yaml files: %s", yml_files)
            # filter the subdirs which has the same name as the
            # files
            subdirs[:] = [d for d in subdirs if d in yml_files]

            logger.debug('sub dirs matching : %s', subdirs)
        return self._parse_tree

    def options(self):
        args = self.parse_tree()
        from ksgen.yaml_utils import to_yaml
        logger.debug(to_yaml("Args: ", args))

        equals_val = '=<val>'
        longest_key = max(args.keys(), key=len)
        key_width = len(longest_key) + len(equals_val)

        options = ""
        for key, option in args.items():
            options += "    --{0:{width}}  {1}\n".format(
                key.replace('/', '-') + equals_val,
                '[' + ', '.join(option['values']) + ']',
                width=key_width
            )
        return options

    def usage(self):
        txt = "    {program} {options} [options] {arguments}"
        options = self._kwargs['repeatable_options'] + [
            '[--%s=<val>...]' % key for key, option in self.parse_tree().items()
            if option[MULTIPLE_ALLOWED]
        ]
        return txt.format(
            program=self._kwargs['program'],
            options=' '.join(options),
            arguments=self._kwargs['arguments'],
        )

    # ### private ###
    def _add_option(self, dir_path, options):
        # remove all data-dirs from the dir_path
        logger.warn("Add option - dir: '%s': %s", dir_path, options)

        dirname = os.path.dirname(dir_path)
        parent_option = self._remove_data_dirs(dirname)

        basename = os.path.basename(dir_path)
        key = os.path.join(parent_option, basename)
        logger.debug("cleaned up arg: '%s': %s", key, options)

        values = key + VALUES
        if key not in self._parse_tree:
            logger.debug("Add new key %s: [%s]", key, ', '.join(options))
            self._parse_tree[values] = options
            self._parse_tree[key + MULTIPLE_ALLOWED] = os.path.exists(
                os.path.join(dir_path, 'multiple'))
        else:
            logger.debug("Update  %s: [%s]", key, ', '.join(options))
            self._parse_tree[values].update(options)

        logger.info("Adding %s: [%s]", key, ', '.join(options))
        logger.info("   key %s:  multiple allowed: %s", key,
                    self._parse_tree[key + MULTIPLE_ALLOWED])

    def _is_data_dir(self, path):
        # is a data dir if  basepath is one of the values of
        # the parent arg_path
        path = os.path.normpath(path)
        basename = os.path.basename(path)
        logger.debug("is '%s' is a data_dir ?", basename)

        # top level dirs are not data dirs
        if os.path.relpath(path, self._config_dir) == basename:
            logger.debug("'%s' is a top_dir, not a data-dir", basename)
            return False

        parent_dir = os.path.dirname(path)
        logger.debug("path: %s, parent_dir: %s", path, parent_dir)
        parent_option = self._remove_data_dirs(parent_dir)
        logger.debug("Checking if '%s' is a data of '%s': %s",
                     basename, parent_option,
                     self._parse_tree[parent_option + VALUES])

        return basename in self._parse_tree[parent_option + VALUES]

    def _remove_data_dirs(self, path):
        """
        Given a path parent-arg/value/child-arg/value/grand-child-arg/...
        returns parent-arg/child-arg/grand-child-arg/...
        """
        arg_path = os.path.relpath(path, self._config_dir)
        logger.debug("args path for %s : %s", path, arg_path)

        dirs = arg_path.split(os.sep)
        args = []    # store parent-dir, child-dir, grand-child-dir

        for d in dirs:
            logger.debug(" .... checking dir: %s", d)
            arg_path_for_dir = os.path.join(*(args + [d]))

            logger.debug(" .... arg path for %s : %s",
                         d, arg_path_for_dir)

            if arg_path_for_dir in self._parse_tree:
                logger.debug(" .... found %s, in parse_trees",
                             arg_path_for_dir)
                args.append(d)
            logger.debug(" .... args: %s", args)
        return os.sep.join(args)
