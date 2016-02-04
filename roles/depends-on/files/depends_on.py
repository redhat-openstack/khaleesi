#!/usr/bin/env python

"""
Fetch dependent changes from gerrit servers and apply them on git repos.

The dependencies are parsed from the GERRIT_CHANGE_COMMIT_MESSAGE environment
variable, which is base64 encoded by the gerrit jenkins module. The format of
the dependencies should be:

Depends-On: <change-id>[@<gerrit-instance>[:<gerrit-port>]]

Where <change-id> is the gerrit Change-Id of the dependent change,
<gerrit-instance> should be a resolvable gerrit instance hostname, and
<gerrit-port> is the port on which gerrit has the ssh interface.

The instance name should be defined in the script's ALLOWED_HOSTS
variable.

Written by Attila Darazs <adarazs@redhat.com>
"""

import base64
import json
import logging
import os
import re
import shlex
import subprocess
import sys
import urlparse
import yaml
from argparse import ArgumentParser
from glob import glob
from jinja2 import Template

# we ignore any other host reference
ALLOWED_HOSTS = ["", "codeng", "review.gerrithub.io:29418"]


def parse_commit_msg(msg=None):
    """Look for dependency links in the commit message."""
    if msg is None:
        msg = os.environ.get("GERRIT_CHANGE_COMMIT_MESSAGE")
    if msg is None:
        logging.warning("GERRIT_CHANGE_COMMIT_MESSAGE is not set")
        return []
    try:
        msg = base64.b64decode(msg)
    except TypeError:
        logging.error("commit message is not base64 encoded: %s", msg)
        return []
    tags = []
    for line in iter(msg.splitlines()):
        # note: this regexp takes care of sanitizing the input
        tag = re.search(r"Depends-On: *(I[0-9a-f]+)@?([0-9a-z\.\-:]*)",
                        line, re.IGNORECASE)
        if not tag:
            continue
        if tag.group(2) not in ALLOWED_HOSTS:
            logging.info("ignoring not allowed host %s", tag.group(2))
            continue
        tags.append([tag.group(1), tag.group(2)])
        logging.debug("valid tag found. Change-Id: %s, host: %s",
                      tag.group(1), tag.group(2))
    return tags


def get_refspec_urls(tags):
    """Parsing the necessary url info for the referenced changes"""
    def_host = os.getenv("GERRIT_HOST", 'review.gerrithub.io')
    def_port = os.getenv("GERRIT_PORT", "29418")
    logging.debug("default gerrit set to %s:%s", def_host, def_port)
    targets = []
    for change, server in tags:
        server = server.split(":")
        if server[0] == "":
            host, port = def_host, def_port
        elif len(server) == 1:
            host, port = server[0], def_port
        else:
            host, port = server[0], server[1]
        cmd = ("ssh -p %s %s \"gerrit query --format json --current-patch-set "
            "change:%s\"") % (port, host, change)
        # we only care about the first line with the json dict
        output = subprocess.check_output(shlex.split(cmd)).splitlines()[0]
        # parse it to json
        data = json.loads(output)

        if "currentPatchSet" not in data:
            logging.warning("failed to fetch data from gerrit for "
                            "Change-Id: %s", change)
            continue
        if data.get("status") not in ["NEW"]:
            logging.warning("Patch already merged "
                            "Change-Id: %s", change)
            continue

        parsed_url = urlparse.urlparse(data["url"])
        # gerrit does not provide the repo URL in the reply, we have to
        # construct it from the clues
        repo_url = "".join([parsed_url.scheme, "://",
                            parsed_url.netloc,
                            # we need the url except the change number
                            parsed_url.path[:parsed_url.path.rfind("/")], "/",
                            data["project"]])
        # get the repo name from the last part after the slash
        repo_folder = data["project"].split("/")[-1]
        repo_ref = data["currentPatchSet"]["ref"]
        repo_branch = data["branch"]

        targets.append([repo_folder, repo_url, repo_ref, repo_branch])
        logging.debug("data query result for Change-Id: %s, server: %s:%s, "
                      "folder %s, url: %s, ref: %s, branch:%s",
                      change, host, port, repo_folder,
                      repo_url, repo_ref, repo_branch)
    return targets


def update_repo(project, url, ref, branch, basedir):
    checkout_cmd = "git checkout FETCH_HEAD"
    try:
        # I didn't find the settings/rpm for the project
        # so I'm going to try to fetch the changes if the
        # directory for that project exists in the tree
        folder_path = os.path.join(basedir, project)
        logging.debug("changing working dir to %s", folder_path)
        os.chdir(folder_path)
        fetch_cmd = "git fetch %s %s" % (url, ref)
        logging.debug("fetch command: %s", fetch_cmd)
        subprocess.Popen(shlex.split(fetch_cmd)).wait()
        subprocess.Popen(shlex.split(checkout_cmd)).wait()
    except OSError:
        logging.warning(
            "Directory not found for {} skipping".format(project)
        )


def update_rpm(project, ref, branch, basedir, ksgen, filenumber):
    output_dict = {}
    # doing a late evaluation on ksgen_settings existence
    # because it might not be needed
    if not ksgen:
        logging.error(
            "ksgen_settings not found"
        )
        sys.exit(1)

    rpm_instructions = glob("{}/khaleesi/settings/rpm/*{}.yml".format(basedir, project))
    if not rpm_instructions:
        logging.warning(
            "khaleesi/settings/rpm/*{}.yml not found in {}".format(project, basedir)
        )
        return

    with open(rpm_instructions[0], "r") as fd:
        # the replace here is important because !lookup is not
        # valid jinja2 template and it will be used later
        output_dict = yaml.load(fd.read().replace("!lookup", ""))

    # do the changes needed for this patch
    output_dict["patch"]["gerrit"]["branch"] = branch
    output_dict["patch"]["gerrit"]["refspec"] = ref

    # but the change still leaves two private urls
    # like private.building.gerrit.url
    # luckly those exist in ksgen_settings and using
    # jinja2 templates here will fill those values
    t = Template(yaml.safe_dump(output_dict, default_flow_style=False))

    with open("{}/khaleesi/extra_settings_{}.yml".format(basedir, filenumber), "w") as fd:
        fd.write(t.render(ksgen))
        fd.write("\n")  # for extra niceness
    logging.warning(
        "wrote {}/khaleesi/extra_settings_{}.yml for {}".format(basedir, filenumber, project)
    )


def generate_config(targets, basedir=".", update=None, ksgenfile=None):
    """
    This works in two ways

    if we know how to build the package (ie. it exists on settings/rpms/)
    we generate one extra_settings_<num>.yml for each of the packages

    if we do not know how to build it but there's a directory with that name
    under basedir we will update that to the ref specified and check that out

    """
    if not ksgenfile:
        ksgenfile = "{}/khaleesi/ksgen_settings.yml".format(basedir)

    try:
        with open(ksgenfile, "r") as fd:
            ksgen = yaml.load(fd)
    except IOError:
        ksgen = None

    filenumber = 1
    for project, url, ref, branch in targets:
        if update == "repo":
            update_repo(project, url, ref, branch, basedir)

        elif update == "rpm":
            update_rpm(project, ref, branch, basedir, ksgen, filenumber)
            filenumber += 1


def test_module(basedir, update, ksgenfile):
    """Test with some known working Change-Ids"""
    test_msg = ("This is a test commit message.\n\n"
                 "Depends-On: If4cea049\n"
                 "Depends-On: Id0aef5ee6dcb@review.gerrithub.io:29418\n"
                 "Depends-On: I1c3f14ba@codeng\n"
                 "Depends-On: I62e3c43afd@codeng\n"
                 "Depends-On: I02c15311@codeng")
    test_tags = parse_commit_msg(base64.b64encode(test_msg))
    test_targets = get_refspec_urls(test_tags)
    generate_config(test_targets, basedir, update, ksgenfile)


def run(basedir, update, ksgenfile):
    logging.warning(
        "getting dependencies for {}".format(update)
    )
    run_tags = parse_commit_msg()
    run_targets = get_refspec_urls(run_tags)
    if run_targets:
        generate_config(run_targets, basedir, update, ksgenfile)
    else:
        logging.warning("Nothing to do. Exiting")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ap = ArgumentParser("Generate changes to repos or rpm settings based on depends-on gerrit comments")
    ap.add_argument('basedir',
                    default=".",
                    help="basedir to work from")
    ap.add_argument('build',
                    default="repo",
                    choices=['repo', 'rpm'],
                    nargs='?',
                    help="What to build")
    ap.add_argument('ksgen_settings',
                    nargs='?',
                    help="where to find the ksgen_settings.yml file")
    args = ap.parse_args()
    run(args.basedir, args.build, args.ksgen_settings)
    # test_module(args.basedir, args.build, args.ksgen_settings)
