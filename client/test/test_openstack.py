#!/usr/bin/env python2.7

from novaclient.v1_1 import client
import os

tenant_id=os.environ['OS_TENANT_ID']
tenant_name=os.environ['OS_TENANT_NAME']
cacert=os.environ['OS_CACERT']
username=os.environ['OS_USERNAME']
password=os.environ['OS_PASSWORD']
auth_url=os.environ['OS_AUTH_URL']

print username
print password
print tenant_id
print tenant_name
print auth_url

c = client.Client(username,password,tenant_name,auth_url)

print dir(c)
print c.flavors.list()
print c.keypairs.list()
