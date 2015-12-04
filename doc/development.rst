Contributing to Khaleesi development
====================================

Getting Started with Khaleesi.
------------------------------

see :ref:`prereqs`

Associated Settings Repository
------------------------------
https://github.com/redhat-openstack/khaleesi-settings

Help, I can't run this thing
----------------------------
Look under the khaleesi/tools/wrappers directory

Code Review (IMPORTANT)
-----------------------

Pull requests will not be looked at on khaleesi github. Code submissions should be done via gerrithub (https://review.gerrithub.io). Please sign up with https://www.gerrithub.io and your github credentials to make submissions. Additional permissions on the project will need to be done on a per-user basis.

When you set up your account on gerrithub.io, it is not necessary to import your existing khaleesi fork.:

    yum install git-review

To set up your repo for gerrit:

Add a new remote to your working tree::

    git remote add gerrit ssh://username@review.gerrithub.io:29418/redhat-openstack/khaleesi

Replace username with your gerrithub username.

Now run::

    git review -s
    scp -p -P 29418 username@review.gerrithub.io:hooks/commit-msg `git rev-parse --git-dir`/hooks/commit-msg

Again, replace username with your gerrithub username.

Required Ansible version
------------------------

Ansible 1.8.2 is now required.

Std{out,err} callback plugin
----------------------------

To use the callback plugin that will log all stdout, stderr, and other data about most tasks, you must set the ANSIBLE_CALLBACK_PLUGINS envvar. You can also set the KHALEESI_LOG_PATH envvar. KHALEESI_LOG_PATH defaults to /tmp/stdstream_logs.:

    export ANSIBLE_CALLBACK_PLUGINS=$WORKSPACE/khaleesi/plugins/callbacks
    export KHALEESI_LOG_PATH=$WORKSPACE/ansible_log

Khaleesi use cases
------------------

Check khaleesi :ref:`usage`


Handling workarounds
--------------------

As OpenStack code and also general tools/libraries from distribution
may contain bugs responsible for blocking installation, running or behaviour
of OpenStack, it can be necessary or very helpfull to implement
workaround for the time while the bug is being properly fixed.

Basically any bug has to be **reported first** in corresponding place
(eg. Red Hat Bugzilla, Launchpad, ...), idealy with
possible workaround described there before implementation in khaleesi happens.

To reflect this there is common style `how to implement workarounds`_,
to support tracking them and obtaining their `bug status overview`_,
and examples for `overriding workaround usage`_ per single run.

How to implement workarounds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1) workaround has to have it's **flag** set **in khaleesi-settings**
   (per product/version/...):

   - in 'workarounds:{}' top level dict
   - flag value should be also dict, with boolean property **enabled** (true|false)
   - has to be named in format ``[bug-tracker-prefix][bug-number-ident]`` where prefixes are:

     - *rhbz* for Red Hat Bugzilla
     - *lp* for Launchpad

   - for example ``workarounds.rhbz1138740.enabled=true``

2) it's **implementation** may be:

   - single task (guarded by ``when: workarounds | bug(flag)`` condition)
   - whole play(s) scoped to group after *group_by* with when condition
   - group name has to be in form `workaround_[flag]` where the flag
     means the key used in *workarounds* settings dictionary (eg. rhbz1138740).
     to not cause confusion with regular groups (imagine usage of group names
     like nova_something etc)

Example of enabling the workaround in settings (same for both following examples)::

    # khaleesi-settings:settings/product/rdo/kilo.yml
    workarounds:
        rhbz1138740:
            desc: "Workaround BZ#1138740: Install nova-objectstore for S3 tests"
            enabled: True
        lp0000001:
            enabled: True


Example of single-task workaround::

    # khaleesi:playbooks/.../some.yml
    # can be some already existing play

    - hosts: somenodes
      tasks:

        # ... snip ... (part of bigger play)
        # you just add one task in the list like following one:

        - fileinline: tempest.conf enable_s3_tests=true
          when: workarounds | bug('rhbz1138740')

Example of multi-task workaround Play (utilizing group_by)::

    # khaleesi:playbooks/.../some.yml
    # ... snip ... following is what you are adding:

    - hosts: controller
      tasks:
        - group_by: key=workaround_rhbz1138740
          when: workarounds| bug('rhbz1138740')

    - name: Workaround BZ#1138740 Install Nova Object Store for S3 tests
      hosts: workaround_rhbz1138740
      tasks:
        - yum: ...
        - service: ...
        ...

Bug status overview
^^^^^^^^^^^^^^^^^^^

For getting overview of currently implemented workarounds, which follow
this guide, You can use helper tool which detects them in the code
and provides more detailed description (fetched from bugtrackers),
to see **all workarounds present in the settings** yamls::

    $ cd khaleesi
    $ ./tools/workaround_status ./settings

    ... list of bugs, their title, state and url, also in which yamls we enable them ...

But as some workarounds can be for older version of OpenStack, and so
marked as resolved in newer versions, this will show warning
that some of the bugs are already closed (as there are settings for older versions too).

So instead of settings folder, You can point it at the **ksgen_settings.yaml**
file to get overview of **workarounds used in specific job run**,
where there normally shouldn't be any workaround for closed bug,
unless it's just freshly resolved and author of the workaround didn't revalidated it yet::
    $ ksgen ...
    $ ./tools/workaround_status ksgen_settings.yaml

    ... partial list of information about bugs,
    ... for just those in use (enabled) for given configuration

Overriding workaround usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Workarounds are enabled by default (based on values in settings),
to disable all of them by force use::

    ksgen ... --extra-vars 'workarounds={}'

to disable (or force enable) specific one::

    ksgen ... --extra-vars '{"workarounds": {"rhbz1138740": {"enabled": true}}}'


Variables meaning
^^^^^^^^^^^^^^^^^

- product.build:
  This variable can come with the following values: `latest`, `ga`, `last_known_good`. It is used to
  construct the path to the images, like:
  `product.images.url.rhos.8-directory.latest.7.2`
- product.full_version:
  The component to test, can be either:
  - OSP: `7`, `7-director`, `8`, `8-director` or
  - RDO: `Juno`, `Kilo`, `Liberty`
- product.core_product_version:
  The major version number of the product, e.g: `7` or `8`.
- product.repo_type:
  Can be either `puddle` or `poodle` for OSP or `delorean` and `deorean_mgt` for RDO.
  - puddle: automatic snapshot of the development repositories (core and OSP-d)
  - poodle: a poodle is a stabilized version of the repository (core only)
  - delorean: a delorean build result or RDO
  - delorean_mgt: a delorean build result of RDO-manager (deprecated)
- product.repo.poodle_pin_version:
  Define a specific version of the poodle. The value can either be `latest` or
  specify a given version like `2015-12-03.1`. The variable is in use only if
  `product.repo_type` is `poodle`.
- product.repo.puddle_pin_version:
  Like for `product.repo.poodle_pin_version` but for a core puddle. The variable is in use only if
  `product.repo_type` is `poodle`.
- product.repo.puddle_director_pin_version:
  The OSP-d puddle version to test. Default is `latest`. This variable is enable only if
  `product.repo_type` is `puddle`.
- product.repo.delorean_pin_version:
  Pin on this dolorean build hash.
