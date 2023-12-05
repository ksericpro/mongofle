# File = local.py
# Author = Eric Ses
# Date = 4/12/2023

# mongo
MONGO_URI = "mongodb://root:ultraman@127.0.0.1:27017/admin"
APP_DB = "fle_demo"
KEYSTORE_COLLECTION = "__keystore"
PERSON_COLLECTION = "person"
SCHEMAS_COLLECTION = "__schemas"

# Hashicorp keys
MASTER_KEY = "key_bytes.bin"
JSON_SCHEMA = "json_schema.json"
VAULT_MODE = "file"

JSON_SCHEMA_MODE = "db"
SECRETS_PATH = 'mongofle'
SECRETS_MASTER = "master"
NORMAL_ROOT_TOKEN ='hvs.fecklRjMDsP0GiflYKmpaONJ'
DOCKER_ROOT_TOKEN = 'hvs.WlVVvB3L2HrGIZvzMhneJTF8'

TOKEN = DOCKER_ROOT_TOKEN

# logs
LOG_FOLDER = "logs"
LOG_MAX_SIZE = 50
LOG_BACKUP = 12