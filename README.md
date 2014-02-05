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


Khaleesi use cases
------------------

You can use Khaleesi to setup these development/testing environments:

* [Foreman](https://github.com/redhat-openstack/khaleesi/blob/master/doc/foreman.md)

* [TripleO Devtest](https://github.com/redhat-openstack/khaleesi/blob/master/doc/tripleo_devtest.md)
