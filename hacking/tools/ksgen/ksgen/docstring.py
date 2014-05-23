try:
    from collections import OrderedDict, Mapping
except ImportError:
    from ordereddict import OrderedDict
    from collections import Mapping
import logging
import os


class Generator(object):
    def __init__(self, config_path):
        self._root_dir = config_path

    def parse_tree(self):
        self._parse_tree = OrderedDict()

        for dir_path, subdirs, files in os.walk(self._root_dir):
            logging.debug("Walking dir: %s", dir_path)
            if dir_path == self._root_dir:
                logging.debug("  ... skipping root dirs")
                continue

            yml_files = set([os.path.splitext(x)[0]
                            for x in files if x.endswith('.yml')])
            logging.debug("  files: %s", yml_files)

            # don't process dirs without yml files
            # but traverse deeper if it is a data dir
            if len(yml_files) == 0:
                if not self._is_data_dir(dir_path):
                    logging.warning("... skipping dir: [%s]: empty dir "
                                    " and not data dir", dir_path)
                    subdirs[:] = []
                else:
                    logging.debug("... skipping: data_dir: %s", dir_path)
                continue

            # add the dir as an option
            self._add_option(dir_path, yml_files)

            logging.debug("yaml files: %s", yml_files)
            # filter the subdirs which has the same name as the
            # files
            subdirs[:] = [d for d in subdirs if d in yml_files]

            logging.debug('sub dirs matching : %s', subdirs)
        return self._parse_tree

    def generate(self):
        args = self.parse_tree()
        logging.debug("args: %s", args)
        doc_string = ""
        for key, value in args.items():
            doc_string += "\n    --{0:24} {1}".format(
                key.replace('/', '-') + "=<val>",
                '[' + ', '.join(value) + ']')
        return doc_string

    # ### private ###
    def _add_option(self, dir_path, values):
        # remove all data-dirs from the dir_path
        logging.info("Add option - dir: '%s': %s", dir_path, values)

        dir_path = os.path.normpath(dir_path)

        dirname = os.path.dirname(dir_path)
        parent_option = self._remove_data_dirs(dirname)

        basename = os.path.basename(dir_path)
        key = os.path.join(parent_option,  basename)
        logging.debug("cleaned up arg: '%s': %s", key, values)

        if key not in self._parse_tree:
            self._parse_tree[key] = values
        else:
            self._parse_tree[key].update(values)

        logging.info("Adding %s: %s", key, values)

    def _is_data_dir(self, path):
        # is a data dir if  basepath is one of the values of
        # the parent arg_path
        path = os.path.normpath(path)
        basename = os.path.basename(path)
        logging.debug("is '%s' is a data_dir ?", basename)

        # top level dirs are not data dirs
        if os.path.relpath(path, self._root_dir) == basename:
            logging.debug("'%s' is a top_dir, not a data-dir", basename)
            return False

        parent_dir = os.path.dirname(path)
        logging.debug("path: %s, parent_dir: %s", path, parent_dir)
        parent_option = self._remove_data_dirs(parent_dir)
        logging.debug("Checking if '%s' is a data of '%s': %s",
                      basename, parent_option,
                      self._parse_tree[parent_option])

        return basename in self._parse_tree[parent_option]

    def _remove_data_dirs(self, path):
        """
        Given a path parent-arg/value/child-arg/value/grand-child-arg/...
        returns parent-arg/child-arg/grand-child-arg/...
        """
        arg_path = os.path.relpath(path, self._root_dir)
        logging.debug("args path for %s : %s", path, arg_path)

        dirs = arg_path.split(os.sep)
        args = []    # store parent-dir, child-dir, grand-child-dir

        for d in dirs:
            logging.debug(" .... checking dir: %s", d)
            arg_path_for_dir = os.path.join(*(args + [d]))

            logging.debug(" .... arg path for %s : %s",
                          d, arg_path_for_dir)

            if arg_path_for_dir in self._parse_tree:
                logging.debug(" .... found %s, in parse_trees",
                              arg_path_for_dir)
                args.append(d)
            logging.debug(" .... args: %s", args)
        return os.sep.join(args)
