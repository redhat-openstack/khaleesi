Handling the Jenkins job definitions
====================================

This section deals with the issue of adding, removing and changing of job
definitions through the JJB files.

A general documentation about JJB can be found on its website_. When in doubt
about what an option means in the job description, search in this manual.

.. _website: http://ci.openstack.org/jenkins-job-builder/

Location and structure
----------------------

The job definitions reside in ``khaleesi-settings/jobs`` and they are in YAML
format. The changes are applied on the official Jenkins server by submitting a
change to the files in this repository, and running the jenkins_job_builder_
job.

.. _jenkins_job_builder: http://rhos-qe-jenkins.rhev-ci-vms.eng.rdu2.redhat.com/job/jenkins_job_builder/

If you removed some job, please make sure to disable or delete the job
that is no longer used. The job has a diff output at the end of the run that
compares the jobs that exist on the server but are not part of the job
definitions.

The ``defaults.yaml`` file containts the default values that all jobs get by
default. It also contains some macros_ that can be referenced later. You
probably don't need to modify this file.

.. _macros: http://ci.openstack.org/jenkins-job-builder/definition.html#macro

At the moment the ``main.yaml`` file contains the definitions for all RDO CI
jobs. On the top of the file you find a **job-template** that is the base of
our jobs. You can see that its name contains a lot of variables in curly
brackets "{}", they are replaced by the actual job definitions, and we give
them values by the **project** definitions lower in the file.

The project definitions are creating a matrix of variables, from which all the
possible combinations get created on the Jenkins server.

Adding new jobs
---------------

The need for a new job could arise when we want to extend our testing. There's
a significant difference between two cases:

* adding a new value to an existing ksgen option (can be thought of as
  extending the testing matrix in an existing dimension)
* adding a new option to ksgen (adding a new dimension to the testing matrix)

The first case is significantly easier to deal with, so let's discuss that
first.

Let's say you added the new variable *foo* for the **distro** setting. If you want to create a whole new set of jobs, then you might want to create a new **project** definition. In most cases, it's enough if you extend an existing definition. In that case, just add the relevant option to the proper place. Here's an example::

    - project:
        name: rhos7-jobs
        product:
                - rhos
            product-version:
                - 7_director
            product-version-repo:
                - poodle
                - puddle
            distro:
                - rhel-7.1
                - foo
            messaging:
                - rabbitmq
    [the rest of the definition is omitted]

If you want to extend the matrix, the changes are more numerous.

* the **job-template** has to be changed, and the new option added to the name
* the *ksgen-builder* macro needs alteration, both in the calling in the job
  template, and in the shell script part (add it to the ksgen command).
* add the option to all the project definitions that are using the template
  (currently all of them), modifying the template name in them too.

This will also result in a replacement of all the Jenkins jobs that use the
template, as the naming changes.


