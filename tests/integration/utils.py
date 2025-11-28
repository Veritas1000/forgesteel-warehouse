import re

import requests

def get_api_token(app_container):
    log = app_container.get_stdout()
    token = re.search(r"^\$1\$[0-9a-f]+$", log, re.MULTILINE)
    return token.group(0) if token is not None else None

def get_auth_token(app_container, api_token):
    url = app_container._create_connection_url()
    connect_headers = {'Authorization': f"Bearer {api_token}"}
    cr = requests.get(f"{url}/connect", headers=connect_headers)
    return cr.json()['access_token']

def get_auth_headers(app_container):
    api_token = get_api_token(app_container)
    access_token = get_auth_token(app_container, api_token)

    headers = {'Authorization': f"Bearer {access_token}"}
    return headers