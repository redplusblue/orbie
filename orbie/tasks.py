from msal import PublicClientApplication

import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.yaml')
with open(CONFIG_PATH, 'r') as config_file:
    CONFIG = yaml.safe_load(config_file)

def get_access_token():
    app = PublicClientApplication(
        client_id=CONFIG['microsoft']['client_id'],
        authority=f"https://login.microsoftonline.com/{CONFIG['microsoft']['tenant_id']}"
    )
    result = app.acquire_token_interactive(scopes=CONFIG['microsoft']['scopes'])
    return result.get("access_token")

import requests

BASE_URL = "https://graph.microsoft.com/v1.0/me/todo/lists"

def get_tasks(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code == 200:
        return response.json()['value']
    else:
        raise Exception(f"Error fetching tasks: {response.status_code}")
