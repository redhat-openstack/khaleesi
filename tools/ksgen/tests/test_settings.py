"""
Usage:
    python test_tree.py <method_name>
    py.test test_tree.py [options]
"""

import os
import pytest
import yaml

from test_utils import TEST_DIR, main
from ksgen.settings import load_configuration


def test_invalid_yml():
    path = os.path.join(TEST_DIR, 'data', 'yml-syntax')

    yaml_path = os.path.join(path, 'dashes.yml')
    with pytest.raises(yaml.scanner.ScannerError):
        load_configuration(yaml_path)

    yaml_path = os.path.join(path, 'spaces.yml')
    with pytest.raises(yaml.parser.ParserError):
        load_configuration(yaml_path)

    yaml_path = os.path.join(path, 'tab.yml')
    with pytest.raises(yaml.scanner.ScannerError):
        load_configuration(yaml_path)

    yaml_path = os.path.join(path, 'map.yml')
    with pytest.raises(TypeError):
        load_configuration(yaml_path)


if __name__ == '__main__':
    main(locals())
