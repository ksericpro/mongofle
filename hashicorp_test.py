# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

# https://hvac.readthedocs.io/en/stable/overview.html

import hvac
import sys

token='hvs.fecklRjMDsP0GiflYKmpaONJ'
   

# Authentication
client = hvac.Client(
    url='http://127.0.0.1:8200',
    token=token,
)

# Info
print("Step 1> Print Info")
print("\tis authenticated=", client.is_authenticated())
print("\tis sealed=", client.sys.is_sealed())

#vault kv get -mount=kv-v2 hello

#print(read_secret_from_vault("hello", token, "foo"))

# Writing a secret
print("Step 2> Write foo=world to 'secret' Secret Engine ")
create_response = client.secrets.kv.v2.create_or_update_secret(
    path='foo',
    secret=dict(baz='world'),
)

print('\tSecret written successfully.')

# Reading a secret
print("Step 3> Read foo from 'secret' Secret Engine ")
read_response = client.secrets.kv.read_secret_version(path='foo', raise_on_deleted_version=True)

print("\t",read_response)
password = read_response['data']['data']['baz']
print("\tpassword={0}".format(password))
