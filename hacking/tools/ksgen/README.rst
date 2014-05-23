ksgen - Khaleesi Settings Generator
===================================

Setup
-----
1. setup virtual env or use existing Khaleesi venv
# source <virtual-env>/bin/activate
# python setup.py develop

Running ksgen
-------------
**assumes** that ksgen is installed, else follow [Setup]_
- start with ksgen --help

Help based on your settings dir
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::
    ksgen --config-dir <dir> help

will display the options you can pass to ksgen to generate the all settings
file.


Running tests
-------------
- pip install pytest

- py.test tests/test_<filename>.py
    or
- python tests/test_<filename>.py  <method_name>

