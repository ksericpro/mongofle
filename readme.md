# Introduction

Mongo FLE with python

## Python setup

python -m pip install "pymongo[encryption,srv]~=3.11"

The second thing you'll need to have installed is mongocryptd, which is an application that is provided as part of 
MongoDB Enterprise.

pip -m venv .env/mongofle
cd .env/mongofle
cd Scripts 
activate
pip -r install requirements.txt

# master key

Note: Storing the master key, unencrypted, on a local filesystem (which is what I do in this demo code) is insecure. In production you should use a secure KMS, such as 
AWS KMS
, 
Azure Key Vault
, or 
Google's Cloud KMS.
, or
Hashicorp Vault

Now you have two keys! One is the 96 random bytes you generated with token_bytes - that's the master key (which remains outside the database). And there's another key in the __keystore collection! This is because MongoDB CSFLE uses 
envelope encryption
. The key that is actually used to encrypt field values is stored in the database, but it is stored encrypted with the master key you generated.

# Running Create Master Key, Schema, Data Key with hashicorp and schema into db

python create_key.py -v=hashicorp -s=db

# Running INference

python fle_main.py -v=hashicorp -s=db

# Hashicorp

## references
[choco] (https://www.liquidweb.com/kb/how-to-install-chocolatey-on-windows/)
[hashicorp] (https://developer.hashicorp.com/vault/tutorials/getting-started/getting-started-install)
[example] (https://developer.hashicorp.com/vault/docs/get-started/developer-qs)
[setup] (https://developer.hashicorp.com/vault/tutorials/getting-started/getting-started-deploy)
[kms] (https://docs.yugabyte.com/preview/yugabyte-platform/security/create-kms-config/hashicorp-kms/)
[kms2] (https://blog.gitguardian.com/how-to-handle-secrets-in-python/)
[vault-docker] (https://gist.github.com/Mishco/b47b341f852c5934cf736870f0b5da81)
[mounting in docker] (https://ioflood.com/blog/docker-compose-volumes-how-to-mount-volumes-in-docker/#:~:text=First%2C%20define%20your%20volume%20in,%3A%2Fpath%2Fin%2Fcontainer%20.)

##  settting vault on docker
docker-compose up

### set enviroment
Linux: export VAULT_ADDR=http://127.0.0.1:8200
or
Windows: set VAULT_ADDR=http://127.0.0.1:8200

OR

## setup
The ./vault/data directory that raft storage backend uses must exist.
mkdir -p ./vault/data

Set the -config flag to point to the proper path where you saved the configuration above.

### command to start
vault server -config=vault/config/config.hcl


## init

## initialize vault
vault operator init

copy down the seal and root token

## unseal
vault operator unseal

for 3 times

Unseal Key (will be hidden):
Key                     Value
---                     -----
Seal Type               shamir
Initialized             true
Sealed                  false
Total Shares            5
Threshold               3
Version                 1.15.1
Build Date              2023-10-20T19:16:11Z
Storage Type            raft
Cluster Name            vault-cluster-72d7028d
Cluster ID              0d5f37ac-526f-27cb-e830-60b3199cc21a
HA Enabled              true
HA Cluster              n/a
HA Mode                 standby
Active Node Address     <none>
Raft Committed Index    31
Raft Applied Index      31

### login
vault login

hvs.fecklRjMDsP0GiflYKmpaONJ

## enable secrets and path kv
vault secrets enable kv-v2

## Checking
vault secrets list

Path          Type         Accessor              Description
----          ----         --------              -----------
cubbyhole/    cubbyhole    cubbyhole_ccc8f7af    per-token private secret storage
identity/     identity     identity_88c3b40a     identity store
kv-v2/        kv           kv_7a040a2a           n/a
secret/       kv           kv_a4995332           n/a
sys/          system       system_30fcbb8e       system endpoints used for control, policy and debugging


## login

Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                hvs.fecklRjMDsP0GiflYKmpaONJ
token_accessor       fJXhwyd5yBFWW8R7be59Ai0a
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]

## open Webui
http://localhost:8200

login via token


## create token for access
vault token create -no-default-policy -policy=trx
WARNING! The following warnings were returned from Vault:

  * Policy "trx" does not exist

Key                  Value
---                  -----
token                hvs.CAESIMGH6ECQ0Cj-56sAV3eXwC3MXP9yG_OA5UOGbXtrXWg-Gh4KHGh2cy56TTdZSTYwdGVDQlJEUnFQREUwclFlaXU
token_accessor       ivAppB1Yat0br010Etv3RPHC
token_duration       768h
token_renewable      true
token_policies       ["trx"]
identity_policies    []
policies             ["trx"]


## CRUD using Vault commands

### Enable kv v2
vault secrets enable secret

### Create
vault kv put secret/hello foo1=world1

#### read
vault kv get -mount=secret hello
vault kv get -mount=secret -field=foo1 hello
vault kv get -mount=secret -format=json hello | jq -r .data.data.baz

### delete
vault kv delete -mount=secret hello
vault kv get -mount=secret hello

## Clean up
Linux:  
pgrep -f vault | xargs kill
rm -r ./vault/data

Windows:
Ctrl C
del ./vault/data

## seal
vault operator seal