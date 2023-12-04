# Hashicorp Example.py
# Author = Eric See
# Date = 4/12/2023
# https://hvac.readthedocs.io/en/stable/overview.html

import hvac
import sys
from secrets import token_bytes
import json
from config import local as _config
import os
import vault_mgr

server = os.environ.get('VAULT_ADDR')
print('server={}'.format(server))

_vaultmgr = vault_mgr.VaultMgr(server, _config.ROOT_TOKEN)
print("Step 1> Connect to Vault")
_vaultmgr.connect_vault()

print("Step 2> Write FLE master key 'secret' Secret Engine ")
# Convert the bytes object back to a string
print("Generate Master Key")
key_bytes = token_bytes(96)
print(type(key_bytes), key_bytes)
decoded_string = key_bytes.decode(_config.ENCODING)
create_response = _vaultmgr.write_secret_to_vault(_config.SECRETS_PATH, 'master', decoded_string)

# Reading a secret
print("Step 3> Read foo from 'secret' Secret Engine ")
read_response = _vaultmgr.read_secret_from_vault(_config.SECRETS_PATH, 'master')
b = bytes(read_response, _config.ENCODING)
print("\tpassword={0}".format(b))
