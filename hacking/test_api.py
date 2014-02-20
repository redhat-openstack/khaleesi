#!/usr/bin/env python

import keystoneclient.v2_0.client as ksclient
import os

#from novaclient import client as nclient
from novaclient.v1_1 import client as nclient

def get_keystone_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['password'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['tenant_name'] = os.environ['OS_TENANT_NAME']
    return d

def get_nova_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']
    return d

creds = get_keystone_creds()
keystone = ksclient.Client(**creds)
print(keystone.auth_token)

nova_creds = get_nova_creds()
print(nova_creds)
nova = nclient.Client(**nova_creds)

#print(nova.servers.list())

#print(nova.floating_ips.list())
#print(nova.images.list())
print(nova.images.get('792470c9-1c43-4dee-b9c5-05aafd81f242').status)
