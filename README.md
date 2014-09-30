Getting Started with Khaleesi
-----------------------
https://github.com/redhat-openstack/khaleesi-settings/blob/master/doc/khaleesi.rst


Associated Settings Repository
-----------------------
https://github.com/redhat-openstack/khaleesi-settings


Code Review (IMPORTANT)
-----------------------

Pull requests will not be looked at on khaleesi github. Code submissions should be done via gerrithub (https://review.gerrithub.io). Please sign up with https://www.gerrithub.io and your github credentials to make submissions. Additional permissions on the project will need to be done on a per-user basis.

When you set up your account on gerrithub.io, it is not necessary to import your existing khaleesi fork.

    yum install git-review

To set up your repo for gerrit:

Add a new remote to your working tree:

    git remote add gerrit ssh://username@review.gerrithub.io:29418/redhat-openstack/khaleesi

Replace username with your gerrithub username.

Now run:

    git review -s
    scp -p -P 29418 username@review.gerrithub.io:hooks/commit-msg `git rev-parse --git-dir`/hooks/commit-msg

Again, replace username with your gerrithub username.

Required Ansible version
------------------------

Ansible 1.5 is now required.


Std{out,err} callback plugin
----------------------------

To use the callback plugin that will log all stdout, stderr, and other data about most tasks, you must set the ANSIBLE_CALLBACK_PLUGINS envvar. You can also set the KHALEESI_LOG_PATH envvar. KHALEESI_LOG_PATH defaults to /tmp/stdstream_logs.

    export ANSIBLE_CALLBACK_PLUGINS=$WORKSPACE/khaleesi/plugins/callbacks
    export KHALEESI_LOG_PATH=$WORKSPACE/ansible_log

Khaleesi use cases
------------------

You can use Khaleesi to setup these development/testing environments:

* [Foreman](https://github.com/redhat-openstack/khaleesi/blob/master/doc/foreman.md)

* [TripleO Devtest](https://github.com/redhat-openstack/khaleesi/blob/master/doc/tripleo_devtest.md)

* [TripleO Tuskar](https://github.com/redhat-openstack/khaleesi/blob/master/doc/tripleo_tuskar.md)


