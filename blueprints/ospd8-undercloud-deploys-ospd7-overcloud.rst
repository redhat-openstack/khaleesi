..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===========================
Deploy a ospd-7 overcloud using an ospd-8 undercloud
===========================

We have some requirements from PM to deploy a ospd-7 overcloud using an
ospd-8 undercloud. PM would like this in CI's status jobs.

Problem description
===================

Consult PM

Proposed change
===============

- Deploy the undercloud
- Remove the tripleo-heat-templates for opsd-8
- Install the tripleo-heat-tempeates for ospd-7
- Rerun ksgen for ospd-8
- Deploy

Alternatives
------------

None

Implementation
==============

Assignee(s)
-----------
whayutin@redhat.com

Milestones
----------

- Deploy the undercloud
- Remove the tripleo-heat-templates for opsd-8
- Install the tripleo-heat-tempeates for ospd-7
- Deploy

Work Items
----------

- test deployment in a dev enviornment
- build POC job
- build new jjb builder, template
- test POC job
- test w/ baremetal
- push to production

Dependencies
============

- The playbooks must be able to be called independently
