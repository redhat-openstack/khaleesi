Community Guidelines:
=====================

Blueprints:
-----------

What is a blueprint?

#. Any new feature requires a blueprint[1].
#. A new feature is anything that changes API / structure of current code and requires a change that spans for more than one file.

 [1] - https://wiki.openstack.org/wiki/Blueprints#Blueprints_reference

Where should one submit blueprints?

#. Any new blueprint requires a discussion in the ML / weekly sync. (we encourage everyone who is involved with the project to join)
#. A code sample / review of a blueprint should use the `git-review -D` for publishing a draft on gerrit.
#. Since the review process is being done as a draft, it is possible to submit the draft prior to an actual ML e-mail.

Reviews:
--------
#. https://review.gerrithub.io/Documentation/config-labels.html#label_Code-Review

#. A "-1"/"-2" from a core requires special attention and a patch should not be merged prior to having the same core remove the "-1"/"-2".

#. In case of a disagreement between two cores, the matter will be brought into discussion on the weekly sync / ML where each core will present his / her thoughts.

#. Self reviews are not allowed. You are required to have at least one more person +1 your code.

#. No review should be merged prior to all gates pass.

#. Bit Rot. To keep the review queue clean an auto-abandoning of dead or old reviews is implemented. A dead review is defined by there are no comments, votes, activity for some agreed upon length of time.  Warning will be posted on the review for two weeks of no activity, after the third week the review will be abandoned.

Gates:
------

#. If a gate has failed, we should first fix that gate and rerun the job to get it passing.

#.  When a gate fails due to an infrastructure problem (example: server timeout, failed cleanup, etc), two cores approval is required in order to remove a gate "-1" vote

Commits:
--------

#. Each commit should be dedicated to a specific subject and not include several patches that are not related.
#. Each commit should have a detailed commit message that describes the "high level" of what this commit does and have reference to other commits in case there is a relationship.

Cores:
------

#. Need to have quality reviews.
#. Reviews are well formed, descriptive and constructive.
#. Reviews are well thought and do not result in a followed revert. (often)
#. Should be involved in the project on a daily basis.
