..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

..
 This template should be in ReSTructured text. The filename in the git
 repository should match the launchpad URL, for example a URL of
 https://bugzilla.redhat.com/show_bug.cgi?id=<rfe_id> should be named
 <rfe_id>.rst .  Please do not delete any of the sections in this
 template.  If you have nothing to say for a whole section, just write: None
 For help with syntax, see http://sphinx-doc.org/rest.html
 To test out your formatting, see http://www.tele3.cz/jbar/rest/rest.html

===========================
Break out overcloud playbooks to match tripleo documentation
===========================

Introduction paragraph -- why are we doing anything?

Problem description
===================

Originally spec'd out as a requirement for dell/dci integration in December 2015.
Search Google docs for dci_dell_khaleesi integration.

Integration:
------------
How can 3rd parties inject a custom workflow?  At the moment 3rd parties to CI
are not able to inject requirements into the ci w/o making a change directly to the code path.

Integration:
------------
Any 3rd party changes are difficult to integrate and test. The complete matrix of
gates must be executed for any change.

Time to results:
----------------
Breaking out a deployment into two parts undercloud and overcloud is not sufficient
when users want to deploy a cloud by hand.  If there is an issue one must start from
the beginning.

Proposed change
===============

The change will breakout the overcloud playbooks to match the sections as described in [1].
A user can follow the code in the playbooks and match it directly to documentation.

[1] http://docs.openstack.org/developer/tripleo-docs/

Alternatives
------------

none propoposed.

Implementation
==============

Assignee(s)
-----------
- wes hayutin
- harry rybacki


Milestones
----------

Target Milestone for completion:

  -  create directory structure that matches the tripleo documentation
  -  move the content of the playbooks into the new playbooks
  -  test virt, and baremetal deployments
  -  test puddle and poodle jobs

Work Items
----------

  - create directory structure that matches the tripleo documentation
  - move the content of the playbooks into the new playbooks
  - test virt, and baremetal deployments
  - test puddle and poodle jobs


Dependencies
============

none
