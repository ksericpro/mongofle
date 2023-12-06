# File = fle_main.py
# Author = Eric Ses
# Date = 4/12/2023

import argparse, os
from pathlib import Path

from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.errors import EncryptionError
from bson import json_util
from config import local as _config

import vault_mgr

if __name__ == '__main__':

   # Get Arguments
   parser = argparse.ArgumentParser()
   parser.add_argument("-v", "--vault", default=_config.VAULT_MODE)
   parser.add_argument("-s", "--schema", default=_config.JSON_SCHEMA_MODE)

   args = parser.parse_args()
   vault_mode = args.vault
   schema_mode = args.schema
   print("vault_mode={}, schema_mode={}".format(vault_mode, schema_mode))

   if vault_mode == "file":
      # Load the master key from 'key_bytes.bin':
      print("Step 1>loading master key from file {}".format(_config.MASTER_KEY))
      key_bin = Path(_config.MASTER_KEY).read_bytes()
   elif vault_mode == "hashicorp":
      server = os.environ.get('VAULT_ADDR')
      print('server={}'.format(server))

      _vaultmgr = vault_mgr.VaultMgr(server, _config.TOKEN)
      print("Step 1> Connect to Vault")
      _vaultmgr.connect_vault()

     # Reading a secret
      print("Step 2> Read foo from 'secret' Secret Engine ")
      read_response = _vaultmgr.read_secret_from_vault(_config.SECRETS_PATH, _config.SECRETS_MASTER)

      print("\treading hex_string=",read_response, type(read_response))
      key_bin = bytes.fromhex(read_response)
      print("\tconvert bytes=",key_bin)
      print("\master key={}".format(key_bin))
      print("\tlength={}".format(len(key_bin)))
            
   # Load the 'person' schema from "json_schema.json":
   print("Step 2>loading schema")

   if schema_mode != "db":
      print("from file")
      collection_schema = json_util.loads(Path(_config.JSON_SCHEMA).read_text())
   else:
      print("from db")
      with MongoClient(_config.MONGO_URI) as client:
         collection_schema = client[_config.APP_DB][_config.SCHEMAS_COLLECTION].find_one()
         # Check if the key 'a' exists in the 'myDict' dictionary.
         if '_id' in collection_schema:
            # If '_id' is in the dictionary, delete the key-value pair with the key 'a'.
            del collection_schema['_id']
   print("\t", collection_schema)      

   # Configure a single, local KMS provider, with the saved key:
   kms_providers = {"local": {"key": key_bin}}

   # Create a configuration for PyMongo, specifying the local master key,
   # the collection used for storing key data, and the json schema specifying
   # field encryption:
   csfle_opts = AutoEncryptionOpts(
      kms_providers,
      "{}.{}".format(_config.APP_DB, _config.KEYSTORE_COLLECTION),
      schema_map={"{}.{}".format(_config.APP_DB, _config.PERSON_COLLECTION): collection_schema},
   )

   # Add a new document to the "person" collection, and then read it back out
   # to demonstrate that the mobile field is automatically decrypted by PyMongo:
   print("Step 3>Encrypt and Insert to MongoDB")
   with MongoClient(_config.MONGO_URI, auto_encryption_opts=csfle_opts) as client:
      client[_config.APP_DB][_config.PERSON_COLLECTION].delete_many({})
      client[_config.APP_DB][_config.PERSON_COLLECTION].insert_one({
         "full_name": "Eric See",
         "gender": "M",
         "married": True,
         "mobile": "+65912345678",
      })
      print("Decrypted find() results: ")
      print("\t",client[_config.APP_DB][_config.PERSON_COLLECTION].find({}))

   # Connect to MongoDB, but this time without CSFLE configuration.
   # This will print the document with mobile *still encrypted*:
   print("Step 4>Find Result in Encrypted")
   with MongoClient(_config.MONGO_URI) as client:
      print("Encrypted find() results: ")
      print("\t", client[_config.APP_DB][_config.PERSON_COLLECTION].find_one())

   # The following demonstrates that if the mobile field is encrypted as
   # "Random" it cannot be filtered:
   print("Step 4>Find Result in Decrypted")
   try:
      with MongoClient(_config.MONGO_URI, auto_encryption_opts=csfle_opts) as client:
         # This will fail if ssn is specified as "Random".
         # in client_schema_create_key.py (and run it again) for this to succeed:
         print("Find by mobile: ")
         print("\t", client[_config.APP_DB][_config.PERSON_COLLECTION].find_one({"mobile": "+65912345678"}))
   except EncryptionError as e:
      # This is expected if the field is "Random" but not if it's "Deterministic"
      print(e)
