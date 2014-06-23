===================================
ksgen - Khaleesi Settings Generator
===================================

Setup
=====
1. Setup virtual env or use existing Khaleesi venv
# source <virtual-env>/bin/activate
# python setup.py develop

Running ksgen
=============
**Assumes** that ksgen is installed, else follow Setup_

help: Show valid options based on settings dir
----------------------------------------------


    ksgen --config-dir <dir> help

displays options you can pass to ksgen to generate_ the all-in-one
settings file.

Using ksgen
===========


How ksgen works
---------------

ksgen is a simple utility to **merge** dictionaries (hashes, mappings), and
lists (sequences, arrays). Any scalar value (string, int, floats) are
overwritten while merging.

For e.g.: merging *first_file.yml* and *second_file.yml*

first_file.yml::

  foo:
    bar: baz
    merge_scalar: a string from first dict
    merge_list: [1, 3, 5]
    nested:
      bar: baz
      merge_scalar: a string from first dict
      merge_list: [1, 3, 5]

and second_file::

  foo:
    too: moo
    merge_scalar: a string from second dict
    merge_list: [3, 5, 2, 4]
    nested:
      bar: baz
      merge_scalar: a string from second dict
      merge_list: [3, 5, 2, 4]

produces the output below::

  foo:
    bar: baz
    too: moo
    merge_scalar: a string from second dict
    merge_list: [1, 3, 5, 3, 5, 2, 4]
    nested:
      bar: baz
      merge_scalar: a string from second dict
      merge_list: [1, 3, 5, 3, 5, 2, 4]


Organizing settings files
--------------------------

ksgen requires a *--config-dir* option which points to the directory where the
settings files are stored. ksgen traverses the *config-dir* to generate a list
of options that sub-commands (**help**, **generate**) can accept.

_`sample settings`:::

  ../settings/
  ├── installer/
  │   ├── foreman/
  │   │   └── network/
  │   │       ├── neutron.yml
  │   │       └── nova.yml
  │   ├── foreman.yml
  │   ├── packstack/
  │   │   └── network/
  │   │       ├── neutron.yml
  │   │       └── nova.yml
  │   └── packstack.yml
  └── provisioner/
      ├── trystack/
      │   ├── tenant/
      │   │   ├── common/
      │   │   │   └── images.yml
      │   │   ├── john-doe.yml
      │   │   ├── john.yml
      │   │   └── smith.yml
      │   └── user/
      │       ├── john.yml
      │       └── smith.yml
      └── trystack.yml


ksgen maps all directories to options and files in those directories to
values that the option can accept. Given the above directory structure,
the options that *generate* can accept are as follows

+---------------------+-----------------------+
|  Options            | Values                |
+=====================+=======================+
|  provisioner        | trystack              |
+---------------------+-----------------------+
|  provisioner-tenant | smith, john, john-doe |
+---------------------+-----------------------+
|  provisioner-user   | john, smith           |
+---------------------+-----------------------+
|  installer          | packstack, foreman    |
+---------------------+-----------------------+
|  installer-network  | nova, neutron         |
+---------------------+-----------------------+

NOTE: ksgen skips provisioner/trystack/tenant/common directory since
there is no *common.yml* file under the tenant directory.

_`generate`: merges settings into a single file
------------------------------------------------
The **generate** command merges multiple settings file into a single
file. This file can then be passed to an ansible playbook. ksgen also
allows merging, extending, overwriting (!overwrite_) and looking up
(!lookup_) settings that ansible (at present) doesn't allow.

merge order
~~~~~~~~~~~
Refering back to the `sample settings`_ above, if you execute the command

::

  ksgen --config-dir sample generate \
    --provisioner trystack \
    --installer packstack \
    --provisioner-user john \
    --extra-vars foo.bar=baz \
    --provisioner-tenant smith \
    output-file.yml

`generate`_ command will create an output-file.yml that include all contents of

+----+---------------------------------------------+--------------------------------------------------+
| SL | File                                        | Reason                                           |
+====+=============================================+==================================================+
| 1  | provisioner/trystack.yml                    | The first command line option                    |
+----+---------------------------------------------+--------------------------------------------------+
| 2  | merge provisioner/trystack/user/john.yml    | The first child of the first command line option |
+----+---------------------------------------------+--------------------------------------------------+
| 3  | merge provisioner/trystack/tenant/smith.yml | The next child of the first command line option  |
+----+---------------------------------------------+--------------------------------------------------+
| 4  | merge installer/packstack.yml               | the next top-level option                        |
+----+---------------------------------------------+--------------------------------------------------+
| 5  | add/merge foo.bar: baz. to output           | extra-vars get processed at the end              |
+----+---------------------------------------------+--------------------------------------------------+

rules-file
~~~~~~~~~~
ksgen arguments can get quite long and tedious to maintain, the options passed
to ksgen can be stored in a rules yaml file to simplify invocation. The command
above can be simplified by storing the options in a yaml file.

rules_file.yml:::

  args:
    provisioner: trystack
    provisioner-user: john
    provisioner-tenant: smith
    installer: packstack
    extra-vars:
      - foo.bar=baz

ksgen generate using rules_file.yml::

  ksgen --config-dir sample generate \
    --rules-file rules_file.yml \
    output-file.yml


Apart from the **args** key in the rules-files to supply default args to
generate, validations can also be added by adding a 'validation.must_have' like
below

::

  args:
    ...
      default args
    ...
  validation:
    must_have:
        - topology

The generate commmand would validate that all options in must_have are supplied
else it will fail with an appropriate message.


yaml tags:
==========

ksgen uses Configure_ python package to keep the yaml files DRY_. It also adds a
few yaml tags like !overwrite, !lookup, !join, !env to the collection.

overwrite
---------
Use overwrite_ tag to overwrite value of a key. This is especially useful when
to clear the contents of an array and add new one

For e.g.: merging

::

  foo: bar

and
::

 foo: [1, 2, 3]

will fail since there is no reasonable way to merge a string and an array.
Use overwrite to set the contents of foo to [1, 2, 3] as below

::

 foo: !overwrite [1, 2, 3]


lookup
-------
Lookup helps keep the yaml files DRY_ by replacing looking up values for keys.

::

 foo: bar
 value_of_foo: !lookup foo

After ksgen process the yaml above the `value_of_foo` will be replaced by
`bar` resulting in the output below.

::

 foo: bar
 value_of_foo: bar


NOTE/Limitation
~~~~~~~~~~~~~~~
Lookup is done only after all yaml files are loaded and the values are merged
so that the entire yaml tree can be searched. This prevents combining other
yaml tags with lookup_ as most tags are processed when yaml is loaded and not
when it is written.

For e.g.:
::

  home: /home/john
  bashrc: !join [ !lookup home, /bashrc ]

**Will fail** to set bashrc to `/home/john/bashrc` where as the snippet below
will work as expected

::

  bashrc: !join [ !env HOME, /bashrc ]


join
-----
Use join tag to join all items in an array into a string. This is quite useful
when using yaml anchors or env_ tag.

::

  unused:
    baseurl: &baseurl http://foobar.com/repo/

  repo:
    epel7: !join[ *baseurl, epel7 ]

  bashrc: !join [ !env HOME, /bashrc ]


env
-----
Use env tag to lookup value of an environment variable. An optional default
value can be passed to the tag. if no default values are passed and the lookup
fails, then a runtime KeyError is generated.

::

 user_home: !env HOME
 user_shell !env [SHELL, zsh]  # default shell is zsh
 job_name_parts:
    - !env [JOB_NAME, 'dev-job']
    - !env [BUILD_NUMBER, None ]

 job_name: "{{ job_name_parts | reject(none) | join('-') }}"


The snippet above effectively uses env_ tag and default option to set the
`job_name` variable to `$JOB_NAME-$BUILD_NUMBER` if they are defined else to
'dev-job'.

Debugging errors in settings
============================
ksgen is heavily logged and by default the log-level is set to warning.
Setting the debug level using the `--debug-level` option to **info** or
**debug** reveals more information about the inner workings of the tool and how
values are loaded from files and merged.


Developing ksgen
=================

Running ksgen unit-tests
------------------------
- pip install pytest

- py.test tests/test_<filename>.py
    or
- python tests/test_<filename>.py  <method_name>

.. _Configure: http://configure.readthedocs.org/en/latest/
.. _DRY: https://en.wikipedia.org/wiki/Don't_repeat_yourself
