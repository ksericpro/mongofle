import os
from pathlib import Path
from secrets import token_bytes

from bson import json_util
from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts
from config import local as _config

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
Path(_config.MASTER_KEY).write_bytes(key_bytes)

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

if _config.JSON_SCHEMA_MODE != "db":
   print("Saving Schema in file")
   json_schema = json_util.dumps(
      schema, json_options=json_util.CANONICAL_JSON_OPTIONS, indent=2
   )
   Path(_config.JSON_SCHEMA).write_text(json_schema)
else:
   print("Saving Schema Collection")
   with MongoClient(_config.MONGO_URI) as client:
      client[_config.APP_DB][_config.SCHEMAS_COLLECTION].insert_one(schema)