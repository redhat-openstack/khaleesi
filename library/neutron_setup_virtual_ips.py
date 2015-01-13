#!/usr/bin/python
from neutronclient.neutron import client
from keystoneclient.v2_0 import client as ksclient

def generate_virtual_ips(foreman_private_address, foreman_public_address):
    public_prefix = ".".join(foreman_public_address.split(".")[0:2])
    private_prefix = ".".join(foreman_private_address.split(".")[0:2])
    admin_prefix = ".".join(foreman_private_address.split(".")[0:2])

    base_public = foreman_public_address.split(".")[3]
    base_private = foreman_private_address.split(".")[3]
    base_admin = foreman_private_address.split(".")[3]


    virtual_ips = {

        "amqp_private": private_prefix + "." + base_private + ".0",

        "ceilometer_public":  public_prefix + "." + base_public + ".1",
        "ceilometer_private":  private_prefix + "." + base_private + ".1",
        "ceilometer_admin":  admin_prefix + "." + base_admin + ".101",

        "cinder_public":  public_prefix + "." + base_public + ".2",
        "cinder_private":  private_prefix + "." + base_private + ".2",
        "cinder_admin":  admin_prefix + "." + base_admin + ".102",

        "db_private": private_prefix + "." + base_private + ".3",

        "glance_public":  public_prefix + "." + base_public + ".4",
        "glance_private":  private_prefix + "." + base_private + ".4",
        "glance_admin":  admin_prefix + "." + base_admin + ".104",

        "heat_public":  public_prefix + "." + base_public + ".5",
        "heat_private":  private_prefix + "." + base_private + ".5",
        "heat_admin":  admin_prefix + "." + base_admin + ".105",

        "heat_cfn_public":  public_prefix + "." + base_public + ".6",
        "heat_cfn_private":  private_prefix + "." + base_private + ".6",
        "heat_cfn_admin":  admin_prefix + "." + base_admin + ".106",

        "horizon_public":  public_prefix + "." + base_public + ".7",
        "horizon_private":  private_prefix + "." + base_private + ".7",
        "horizon_admin":  admin_prefix + "." + base_admin + ".107",

        "keystone_public":  public_prefix + "." + base_public + ".8",
        "keystone_private":  private_prefix + "." + base_private + ".8",
        "keystone_admin":  admin_prefix + "." + base_admin + ".108",

        "loadbalancer_private" : private_prefix + "." + base_private + ".9",

        "neutron_public":  public_prefix + "." + base_public + ".10",
        "neutron_private":  private_prefix + "." + base_private + ".10",
        "neutron_admin":  admin_prefix + "." + base_admin + ".110",


        "nova_public":  public_prefix + "." + base_public + ".11",
        "nova_private":  private_prefix + "." + base_private + ".11",
        "nova_admin":  admin_prefix + "." + base_admin + ".111",

        "swift_public":  public_prefix + "." + base_public + ".12",
        "swift_internal":  private_prefix + "." + base_private + ".12",
    }

    return public_prefix, private_prefix, virtual_ips
    #controller_name : "HAcontroller"
    #controller_ip : keystone_public_vip
    #controller_priv_ip : keystone_private_vip
    #controller_pub_ip : keyst0one_public_vip
    #}

def neutron_allowed_pairs(username, password, tenant, auth_url, public_prefix, private_prefix):
    kclient = ksclient.Client(username=username,password=password,tenant_name=tenant, auth_url=auth_url)
    endpoint = kclient.service_catalog.url_for(service_type='network', endpoint_type='publicURL')

    token = kclient.auth_token
    kwargs = {'token': token, 'endpoint_url': endpoint }
    neutron = client.Client('2.0', **kwargs)

    ports = neutron.list_ports()

    request_body = {"port": {"allowed_address_pairs": [{"ip_address": private_prefix + ".0.0/16"}, {"ip_address": public_prefix + ".0.0/16"}]}}

    for port in ports['ports']:
        neutron.update_port(port["id"], body=request_body)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            username     =   dict(required=True),
            password     =   dict(required=True),
            tenant      =   dict(required=True),
            auth_url      =   dict(required=True),
            foreman_private_address     =   dict(required=True),
            foreman_public_address      =   dict(required=True),
        )
    )

    public_prefix, private_prefix, virtual_ips = generate_virtual_ips(module.params['foreman_private_address'],module.params['foreman_public_address'])
    neutron_allowed_pairs(module.params['username'], module.params['password'], module.params['tenant'], module.params['auth_url'], public_prefix, private_prefix)

    ansible_facts={ 'virtual_ips' : virtual_ips}
    module.exit_json(changed=True, ansible_facts=ansible_facts)

from ansible.module_utils.basic import *
main()

