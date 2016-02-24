#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2016, Adriano Petrich <apetrich@redhat.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: tls_tht
version_added: "1.9"
short_description: Generate the tht templates for enabled ssl
description:
   - Generate the tht templates for enabled ssl
options:
    source_dir:
        description:
            - directory to copy the templates from
        required: false
        default: "/usr/share/openstack-tripleo-heat-templates/"
    dest_dir:
        description:
            - were to copy the files to
        required: false
        default: ""
    cert_filename:
        description:
            - the cert pem filename
        required: false
        default: cert.pem
    cert_ca_filename:
        description:
            - the key pem filename
        required: false
        default: key.pem
    key_filename:
        description:
            - the CA cert pem filename
        required: false
        default: cert.pem


'''

EXAMPLES = '''
# Generate the tht templates for enabled ssl
- tls_tht:
'''

import yaml
from ansible.module_utils.basic import *  # noqa


def _open_yaml(filename):
    with open(filename, "r") as stream:
        tmp_dict = yaml.load(stream)
    return tmp_dict


def create_enable_file(certpem, keypem, source_dir, dest_dir):
    output_dict = _open_yaml("{}environments/enable-tls.yaml".format(source_dir))

    for key in output_dict["parameter_defaults"]["EndpointMap"]:
        if output_dict["parameter_defaults"]["EndpointMap"][key]["host"] == "CLOUDNAME":
            output_dict["parameter_defaults"]["EndpointMap"][key]["host"] = "IP_ADDRESS"

    output_dict["parameter_defaults"]["SSLCertificate"] = certpem
    output_dict["parameter_defaults"]["SSLKey"] = keypem

    output_dict["resource_registry"]["OS::TripleO::NodeTLSData"] = \
        "{}/puppet/extraconfig/tls/tls-cert-inject.yaml".format(source_dir)

    with open("{}enable-tls.yaml".format(dest_dir), "w") as stream:
        yaml.safe_dump(output_dict, stream, default_style='|')


def create_anchor_file(cert_ca_pem, source_dir, dest_dir):
    output_dict = _open_yaml(
        "{}environments/inject-trust-anchor.yaml".format(source_dir)
    )

    output_dict["parameter_defaults"]["SSLRootCertificate"] = cert_ca_pem

    output_dict["resource_registry"]["OS::TripleO::NodeTLSCAData"] = \
        "{}/puppet/extraconfig/tls/ca-inject.yaml".format(source_dir)

    with open("{}inject-trust-anchor.yaml".format(dest_dir), "w") as stream:
        yaml.safe_dump(output_dict, stream, default_style='|')


def main():
    module = AnsibleModule(
        argument_spec=dict(
            source_dir=dict(default="/usr/share/openstack-tripleo-heat-templates/",
                            required=False),
            dest_dir=dict(default="", required=False),
            cert_filename=dict(default="cert.pem", required=False),
            cert_ca_filename=dict(default="cert.pem", required=False),
            key_filename=dict(default="key.pem", required=False),
        )
    )

    with open(module.params["cert_filename"], "r") as stream:
        certpem = stream.read()

    with open(module.params["cert_ca_filename"], "r") as stream:
        cert_ca_pem = stream.read()

    with open(module.params["key_filename"], "r") as stream:
        keypem = stream.read()

    create_enable_file(certpem, keypem, module.params["source_dir"], module.params["dest_dir"])
    create_anchor_file(cert_ca_pem, module.params["source_dir"], module.params["dest_dir"])
    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
