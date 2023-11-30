storage "raft" {
  path    = "./vault/data"
  node_id = "node1"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = "true"
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"
ui = true
disable_mlock = true
default_lease_ttl = "768h"
max_lease_ttl = "8760h"

path "transit/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/token/lookup-self" {
        capabilities = ["read"]
}

path "sys/capabilities-self" {
        capabilities = ["read", "update"]
}

path "auth/token/renew-self" {
        capabilities = ["update"]
}

path "sys/*" {
        capabilities = ["read"]
}
