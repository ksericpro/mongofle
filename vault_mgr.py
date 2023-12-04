# vault_mgr.py
# Author = Eric See
# Date = 4/12/2023
# https://hvac.readthedocs.io/en/stable/overview.html

import hvac
import sys
import os
import boto3

class VaultMgr:
    def __init__(self, server, token):
        self.name = "Vault Mgr"
        self.server = server
        self.token = token     

    def connect_vault(self):
        print("{}:Connecting to {}".format(self.name,self.server))
        self.client = hvac.Client(
        url=self.server, token=self.token)
        print("{}:is authenticated={}".format(self.name, self.client.is_authenticated()))
        print("{}is sealed={}".format(self.name, self.client.sys.is_sealed()))


    def fetch_secret_from_aws(self, secret_name):
        try:
            session = boto3.session.Session()
            client = session.client(service_name='secretsmanager', region_name='us-east-1')
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            return get_secret_value_response['SecretString']
        except Exception as e:
            print(e)
            return None
       
    def create_secret_in_aws(self, secret_name, secret_value):
        try:
            session = boto3.session.Session()
            client = session.client(service_name='secretsmanager', region_name='us-east-1')
            client.create_secret(Name=secret_name, SecretString=secret_value)
            return True
        except Exception as e:
            print(e)
            return False
   
    def read_secret_from_vault(self, secret_path, secret_name):
        try:
           read_response = self.client.secrets.kv.read_secret_version(path=secret_path, raise_on_deleted_version=True)
           #return read_response
           return read_response['data']['data'][secret_name]
        except Exception as e:
           print(e)
           return None

    def write_secret_to_vault(self, secret_path, secret_name, secret_value):
        try:
            create_response = self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,
                secret={secret_name: secret_value},
            )
            print('{}:Secret written successfully.'.format(self.name))
            return create_response
        except Exception as e:
            print(e)
            return None
