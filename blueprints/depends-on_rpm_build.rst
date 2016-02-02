..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode


===========================
rpm build for depends-on
===========================

Depends-on functionality is broken at this moment.


Problem description
===================

If a comment on a patch has a depends-on: <hash>[:codeng]

It is supposed to get those patchs and add to the current run. For exemple is a tripleoclient needs

a review from tht it is expected that we will gate the tripleoclient with a patched tht with that review.

But, right now that funtionality is not working. As we are no longer building on repos under a git

clone on the {{ base_dir }} the way that depends-on is doing right now does not work. What we need

is for it to use the patch-rpm and build package playbook to create the packages so we can upload

it to the test run. Furthermore to make things more complicated there are two kinds of depends-on.

The filepath-related changes like when a patch depends on another patch from khaleesi and

khaleesi-settings and the rpm-related when a patch depends on a change on another rpm


Proposed change
===============


The idea is to split the depends-on playbook into two playbooks

depends-on-repo
---------------

That it will update the current HEAD of the repos under the base_dir


depends-on-rpm
--------------

This will generate an extra small ksgen_settings.yml probably called extra_settings_{{num}}.yml

that is going to be passed together with ksgen_settings.yml

The extra_settings_<num>.yml would be jus the needed change to the ksgen_settings and it would be

something like:


.. code-block:: yaml
    gating_repo: openstack-tripleo-heat-templates
    patch:
      dist_git:
        branch:
          7-director: rhos-7.0-pmgr-rhel-7
          8-director: rhos-8.0-director-rhel-7
        name: openstack-tripleo-heat-templates
        url: 'http://pkgs.devel.redhat.com/cgit/rpms/openstack-tripleo-heat-templates'
      gerrit:
        branch: rhos-7.0-patches  # the filled up branch from the dependend review
        name: gerrit-openstack-tripleo-heat-templates
        refspec: refs/changes/41/65241/9 # the filled up refspec from the dependend review
        url: 'https://code.engineering.redhat.com/gerrit/openstack-tripleo-heat-templates'
      upstream:
        name: upstream-openstack-tripleo-heat-templates
        url: https://git.openstack.org/openstack/tripleo-heat-templates


So a job would look like this:


.. code-block:: bash
    # fetch dependent gating changes for khaleesi and khaleesi-settings
    if [ $GERRIT_CHANGE_COMMIT_MESSAGE ]; then
        ansible-playbook -i local_hosts -vv playbooks/depends-on-repo.yml
    fi

    # generate config
    ksgen --config-dir settings generate \

        ... yada yada yada

        --extra-vars @../khaleesi-settings/settings/product/rhos/private_settings/redhat_internal.yml \
        ksgen_settings.yml

    # fetch dependent gating changes for related rpms
    if [ $GERRIT_CHANGE_COMMIT_MESSAGE ]; then
        ansible-playbook -i local_hosts -vv playbooks/depends-on-rpm.yml
    fi

    for extra_settings in extra_settings_*.yml; do
        if [ -e "$extra_settings" ] ; then
          ansible-playbook -vv --extra-vars @ksgen_settings.yml  --extra_vars @$extra_settings -i local_hosts playbooks/build_gate_rpm.yml;
        fi;
    done
    #now the built rpms are in the base_dir/generated_rpms/*.rpm

    ... continue with the deployment ...


The second extra-vars will overwrite the common parameters of the ksgen_settings allowing us to

build multiple packages The downside is that it will only work for the packages that we know how

to build rpms.


Implementation
==============

Assignee(s)
-----------

Primary assignee:

  apetrich@redhat.com


