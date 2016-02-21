..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode


=========================
Component default tester
=========================

Implement default environment and parameters for component testing.

Problem description
===================

It's not possible to run tests in component that doesn't include jenkins-config
yml file.

jenkins-config isn't included in upstream component repos and writing one is
not an simple task (even copy a sample might not be as easy as one may imagine)

So anyone who picks up khaleesi and running the most simple tester (pep8) will
have failures only due to missing jenkins-config file.

Proposed change
===============

Use default variables in case a jenkins config file couldn't be found
in component repo.

default invocation will be similar to upstream invocation:
- install pip packages based on test-requirements and requirements files
- use tox to start running the tests

Alternatives
------------

Force jenkins-config implementation in every project tested with khaleesi.

Pros:
    - Well defined structure that already tested and verified
Cons:
    - Requires the user to write it
    - Prevents 'out of the box' usage of Khaleesi

Implementation
==============

Assignee(s)
-----------

Arie Bregman

Milestones
----------

Target Milestone for completion:

  M1. Proof of Concept - upload change that enable default testing
  M2. Design for Production - design how the default invocation will work
  M3. Implementation
  M4. Production deployment


Work Items
----------

- Submit a patch that:
   * Include default variables for component configuration
   * Loads config file variables by order:
       - component config file
       - default variables

After running the tests, Khaleesi should keep running the same tasks for
both invocations ( default and jenkins-config based)

Dependencies
============

None
