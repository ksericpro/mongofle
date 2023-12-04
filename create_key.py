# Hashicorp create_key.py
# Author = Eric Ses
# Date = 4/12/2023

import argparse, os
from pathlib import Path
from secrets import token_bytes

from bson import json_util
from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts
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

   # Generate a secure 96-byte secret key:
   print("Generate Master Key")
   key_bytes = token_bytes(96)

   # Configure a single, local KMS provider, with the saved key:
   kms_providers = {"local": {"key": key_bytes}}
   csfle_opts = AutoEncryptionOpts(
      kms_providers=kms_providers, key_vault_namespace="{}.{}".format(_config.APP_DB, _config.KEYSTORE_COLLECTION)
   )

   # Connect to MongoDB with the key information generated above: sa:l4UrHkS8kupd4ptF
   with MongoClient(_config.MONGO_URI, auto_encryption_opts=csfle_opts) as client:
      print("Resetting database & keystore ...")
      client.drop_database(_config.APP_DB)

      # Create a ClientEncryption object to create the data key below:
      client_encryption = ClientEncryption(
         kms_providers,
         "{}.{}".format(_config.APP_DB, _config.KEYSTORE_COLLECTION),
         client,
         CodecOptions(uuid_representation=STANDARD),
      )

      print("Creating key in keystore collection ...")
      key_id = client_encryption.create_data_key("local", key_alt_names=["example"])

   # writing to file
   if vault_mode == 'file':
      print("Writing Master key to file {}".format(_config.MASTER_KEY))
      Path(_config.MASTER_KEY).write_bytes(key_bytes)
   elif vault_mode == 'hashicorp':
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


   schema = {
   "bsonType": "object",
   "properties": {
         "mobile": {
            "encrypt": {
               "bsonType": "string",
               # Change to "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic" in order to filter by ssn value:
               #"algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
               "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
               "keyId": [key_id],  # Reference the key
            }
         },
      },
   }

   if schema_mode != "db":
      print("Saving Schema in file")
      json_schema = json_util.dumps(
         schema, json_options=json_util.CANONICAL_JSON_OPTIONS, indent=2
      )
      Path(_config.JSON_SCHEMA).write_text(json_schema)
   else:
      print("Saving Schema Collection in MongoDB")
      with MongoClient(_config.MONGO_URI) as client:
         client[_config.APP_DB][_config.SCHEMAS_COLLECTION].insert_one(schema)