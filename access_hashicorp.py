# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

import hvac
import sys

# Authentication
client = hvac.Client(
    url='http://127.0.0.1:8200',
    token='hvs.fecklRjMDsP0GiflYKmpaONJ',
)



# Writing a secret
# vault kv put -mount=secret my-secret-password password=Hashi123

create_response = client.secrets.kv.v2.create_or_update_secret(
    path='my-secret-password',
    secret=dict(password='Hashi123'),
)

print('Secret written successfully.')

# vault kv put -mount=secret my-secret-password password=123
create_response = client.secrets.kv.v2.create_or_update_secret(
    path='my-secret-password',
    secret=dict(password='123'),
)

print('Secret written successfully.')

# Reading a secret
# vault kv get -mount=secret my-secret-password
read_response = client.secrets.kv.read_secret_version(path='my-secret-password', raise_on_deleted_version=True)

password = read_response['data']['data']['password']
print("password={0}".format(password))

#if password != 'Hashi123':
#    sys.exit('unexpected password')

print('Access granted!')