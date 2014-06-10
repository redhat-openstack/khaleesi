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

ksgen uses Configure python package to keep the yaml files DRY. It also adds a
few yaml tags like !overwrite, !lookup, !join to the collection.

!overwrite
----------

!lookup
-------

!join
-----

Developing ksgen
=================

Running ksgen unit-tests
------------------------
- pip install pytest

- py.test tests/test_<filename>.py
    or
- python tests/test_<filename>.py  <method_name>

