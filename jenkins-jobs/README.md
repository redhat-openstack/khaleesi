These are the job definitions for the [ci.centos.org system][1].

You can replicate the jobs by installing Jenkins Job Builder (JJB):

    pip install jenkins-job-builder

Create your config.ini from config.ini.sample, according to your
Jenkins configuration, then create/update the jobs with:

    jenkins-jobs --conf config.ini update .

Further information about how to alter these files can be found at
[JJB documentation][2].

Note: There are a number of Jenkins plugins necessary to run these jobs
with full functionality. Compare the definitions with the documentation
to find out the currently required set of extra plugins.

[1]: https://ci.centos.org/view/rdo/
[2]: http://ci.openstack.org/jenkins-job-builder/
