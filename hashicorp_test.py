# File =hashicorp_test.py
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
import base64

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
print("\tlength={}".format(len(key_bytes)))
hex_string = bytes(key_bytes).hex()
print("\twriting hex_string=",hex_string)

create_response = _vaultmgr.write_secret_to_vault(_config.SECRETS_PATH, _config.SECRETS_MASTER, hex_string)

# Reading a secret
print("Step 3> Read foo from 'secret' Secret Engine ")
read_response = _vaultmgr.read_secret_from_vault(_config.SECRETS_PATH, _config.SECRETS_MASTER)

print("\treading hex_string=",read_response, type(read_response))
b = bytes.fromhex(read_response)
print("\tconvert bytes=",b)
print("\master key={}".format(b))
print("\tlength={}".format(len(b)))