import json, yaml

with open("../config/config.yaml", 'r') as config_file:
    config = yaml.safe_load(config_file)

with open ("../config/secrets.json", 'r') as secrets_file:
    secret = json.load(secrets_file)

def get_config():
    """
    Returns the config dictionary from the config.yaml file in the config directory
    :return: Dictionary of config values
    """
    return config

def get_secret():
    """
    Returns the secret dictionary from the secrets.json file in the config directory
    :return: Dictionary of secret values
    """
    return secret
