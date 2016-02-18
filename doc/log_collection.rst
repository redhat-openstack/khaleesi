Log collection in Khaleesi
==========================

Collecting and saving the logs after a job run from the affected machines is an
important step. Khaleesi has a playbook dedicated for this process.

To collect the logs from the machines, run the
``khaleesi/playbooks/collect_logs.yml`` playbook right after the job run with
the same settings and host file. The localhost and the machine called ``host0``
is excluded from the log collection. They are usually long running machines
(the slave and if it exists, a virtual host) that have a large amount and
mostly irrelevant logs.

What files are gathered?
------------------------

Quite a few diagnostic commands are run on the machines (found in the playbook)
and then a set of log files collected. If some specific setting used require
specific logs to be collected, it's practical to add these files to that
specific settings yaml::

    job:
        archive:
            - /var/foo/*.log
            - /var/bar/engine.log
            - /opt/baz/*.xml
            ...

If any file is missing it won't cause the log collection to fail.

Methods of gathering logs
-------------------------

By default the logs are stored on the machine running ansible in
``khaleesi/collected_files``, each machine's log in a different ``tar.gz``
file.

This behavior can be changed by the ``--logs=gzip`` option, which will result
in individually gzipping the files instead.

Uploading the logs
------------------

When using the gzip method, it's possible to upload the logs on an artifact
server. Ideally the logs are then exposed on a HTTP server for online browsing.

To set up a new site, add a new option to ``khaleesi/settings/logs/gzip/site``,
then use the ``--logs-site`` option when running ksgen.

An example site definition looks like::

    job:
        rsync_logs: true
        rsync_path: myuser@example.com:/opt/artifacts
        artifact_url: http://example.com/artifacts

The ``rsync_path`` should be something that rsync understands as a destination,
and the ``artifact_url`` will be used to generate the link to the logs. This
method assumes the job runs on a Jenkins server, so the ``$BUILD_TAG`` variable
should be set in the environment.

After the upload, the logs are deleted from the local machine and a link file
is created as ``khaleesi/collected_files/full_logs.html``. This file should be
added as an artifact to the Jenkins job definition and can be used as a one
click redirect to the job specific artifacts.

Setting up an artifact storage
------------------------------

The machine running the job should be able to upload the logs without a
password to the artifact server. When using Apache to expose the logs for
browsing, the following httpd settings will allow transparent browsing of the
gzipped files::

    Alias /artifacts /opt/artifacts

    <Directory /opt/artifacts>
        Options +Indexes
        RewriteCond   %{HTTP:Accept-Encoding} gzip
        RewriteCond   %{LA-U:REQUEST_FILENAME}.gz -f
        RewriteRule   ^(.+)$ $1.gz [L]
        <FilesMatch ".*\.gz$">
            ForceType text/plain
            AddDefaultCharset UTF-8
            AddEncoding x-gzip gz
        </FilesMatch>
    </Directory>

It's recommended to put these settings to a separate file in the
``/etc/httpd/conf.d`` directory.

Pruning old logs
----------------

The artifact directory could grow too big over time, thus it's useful to set up
a cron job for deleting obsolete logs.

On the artifact server, add a line to /etc/crontab similar to this::

    0 0 * * * rhos-ci find /opt/artifacts -maxdepth 1 -type d -ctime +14 -exec rm -rf {} +;

This will delete any artifact directory in /opt/artifacts that is older than 14
days. It's useful to match the Jenkins artifact retention time with the time
specified here to avoid broken links in Jenkins.

Use in Jenkins job definitions
------------------------------

To use the advanced gzip+upload method, modify your jobs the following way:

Add ``--logs=gzip --logs-site=mysite`` to the ksgen invocation of your builder, for example::

    ksgen --config-dir settings generate \
        --provisioner=manual \
        ...
        --logs=gzip \
        --logs-site=downstream \
        ...
        ksgen_settings.yml

Add ``**/full_logs.html`` to the list of artifacts::

    - publisher:
        name: default-publishers
        publishers:
            - archive:
                artifacts: '**/collect_logs.txt, **/cleanup.txt, **/nosetests.xml, **/ksgen_settings.yml, **/full_logs.html'

After regnerating the jobs, the logs should start appearing on the artifact server.

It's practical to match the Jenkins artifact retention time with the artifact
server retention time to avoid broken links in Jenkins::

    - defaults:
        name: job-defaults
        ...
        logrotate:
            daysToKeep: 14
            artifactDaysToKeep: 14
        ...
