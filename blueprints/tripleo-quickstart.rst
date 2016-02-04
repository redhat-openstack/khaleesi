..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode


===========================
Replace instack-virt-setup with tripleo quickstart
===========================

instack-virt-setup is the official way to setup a poc virt environment for tripleo [1]

A replacement for instack-virt-setup has been adopted by the rdo community [2][3]


[1] http://tripleo.org/environments/environments.html#virtual-environment
[2] https://www.rdoproject.org/rdo-manager/
[3] https://github.com/redhat-openstack/tripleo-quickstart

Problem description
===================

instack-virt-setup itself is not tested in tripleo, nor is it supported downstream.
It's not an idempotent setup of the tripleo environement and it's also not very configurable.


Proposed change
===============

- Add support for executing the tripleo quickstart to setup the undercloud and overcloud
nodes in virtual environments and then hand off to khaleesi for the overcloud deployment.

- Update tripleo quickstart to work with the downstream ospd content.

- Once completed this work will bring the downstream virtual deployments in line with the accepted
upstream virtual deployment

- For puddle's the goal is to have an undercloud appliance that is simply imported and started.
The appliance will be built with the quickstart playbooks.

- In the tripleo, rdo, or poodle workflow, if patches or updates need to be applied to the
undercloud appliance, the quickstart is already built to handle updates.

- Provide a community standard for building the undercloud when needed. It will be much easier
to push this standard if the code is single purpose and not commingled with khaleesi.

- Other tools whether they be ansible, python, or shell based can all interface with khaleesi
via the hosts and ssh config file. A well defined interface into khlaeesi than try to
include *everything* in khaleesi itself may prove to be valuable.

Alternatives
------------

Create other tools and workflows that call libvirtd to stand up and provision virt environments
for rdo-manager/ospd

- libvirt implementations, e.g. https://review.gerrithub.io/#/c/259615/

- no-op or manual

Implementation
==============

Assignee(s)
-----------

myoung@redhat.com
sshnaidm@redhat.com
whayutin@redhat.com
trown@redhat.com


Primary assignee:

  RDO: sshnaidm@redhat.com
  OSPD: myoung@redhat.com

Milestones
----------

Target Milestone for completion:

  M1. Proof of Concept - create beta code and jobs to test tripelo quickstart
  M2. Proof of Concept - create a branch of tripleo quickstart for downstream ospd use
  M3. Design for Production - create a design for upstream/downstream quickstart
  M4. Implementation
  M5. Production deployment


Work Items
----------

Work items or tasks -- break the feature up into the things that need to be
done to implement it. Those parts might end up being done by different people,
but we're mostly trying to understand the time line for implementation.

   - POC rdo-manager job that executes the khaleesi provisioner, tripleo quickstart to setup the
      undercloud,  and hands off to khaleesi for the overcloud deployment, test and log collection.
   - JJB created for rdo-manager jobs in ci.centos for the above workflow
   - A ospd-7 undercloud qcow is created
   - The tripleo quickstart is branched for ospd and updated to use the downstream yum repos and
      adjustments are made for ospd-7 and ospd-8
   - A POC ospd job that executes the khaleesi provisioner, tripleo quickstart (ospd) to setup the
      undercloud, and hands off to khaleesi for the overcloud deployment.
   - A design is created  for tripleo quickstart to elegently and efficently handle the subtle differences
      between setting up rdo-manager and ospd director for all the supported versions.
   -  The design for M6 is implemented
   - tripleo quickstart is formally supported in CI


Dependencies
============


