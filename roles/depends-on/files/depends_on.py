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

# we ignore any other host reference
ALLOWED_HOSTS = ["", "codeng"]

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
        targets.append([repo_folder, repo_url, repo_ref])
        logging.debug("data query result for Change-Id: %s, server: %s:%s, "
                      "folder %s, url: %s, ref: %s",
                      change, host, port, repo_folder, repo_url, repo_ref)
    return targets

def checkout_changes(targets, basedir="."):
    """Fetch and checkout the changes for the target repos"""
    checkout_cmd = "git checkout FETCH_HEAD"
    for folder, url, ref in targets:
        folder_path = os.path.join(basedir, folder)
        logging.debug("changing working dir to %s", folder_path)
        os.chdir(folder_path)
        fetch_cmd = "git fetch %s %s" % (url, ref)
        logging.debug("fetch command: %s", fetch_cmd)
        subprocess.Popen(shlex.split(fetch_cmd)).wait()
        subprocess.Popen(shlex.split(checkout_cmd)).wait()

def test_module():
    """Test with some known working Change-Ids"""
    test_msg = ("This is a test commit message.\n\n"
                 "Depends-On: If4cea049\n"
                 "Depends-On: I1c3f14ba@codeng")
    test_tags = parse_commit_msg(base64.b64encode(test_msg))
    test_targets = get_refspec_urls(test_tags)
    checkout_changes(test_targets, "/tmp")

def run(repo_dir):
    run_tags = parse_commit_msg()
    run_targets = get_refspec_urls(run_tags)
    checkout_changes(run_targets, repo_dir)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        print "Usage: %s <repo-directory>" % (sys.argv[0])
    else:
        run(sys.argv[1])
        #test_module()
