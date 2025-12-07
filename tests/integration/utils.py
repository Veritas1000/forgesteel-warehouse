import re
from typing import Dict

import requests

def get_api_token(app_container):
    log = app_container.get_stdout()
    token = re.search(r"^\$1\$[0-9a-f]+$", log, re.MULTILINE)
    return token.group(0) if token is not None else None

def get_csrf_token(app_container, api_token, requests_session):
    url = app_container._create_connection_url()
    connect_headers = {'Authorization': f"Bearer {api_token}"}
    cr = requests_session.post(f"{url}/connect", headers=connect_headers)
    
    token = get_csrf_access_token_from_response(cr)
    return token

def get_csrf_headers(app_container, requests_session):
    api_token = get_api_token(app_container)
    token = get_csrf_token(app_container, api_token, requests_session)

    headers = {'X-CSRF-TOKEN': token}
    return headers

def get_csrf_access_token_from_response(response: requests.Response) -> str | None:
    csrf_cookie = get_cookie_from_response(response, 'csrf_access_token')
    token = csrf_cookie['csrf_access_token'] if csrf_cookie is not None else None
    return token

def get_cookie_from_response(response: requests.Response, cookie_name: str) -> Dict[str, str] | None:
    cookie_headers = response.headers.get("Set-Cookie")
    if cookie_headers is None:
        return None
    
    for header in cookie_headers.split(','):
        attributes = header.split(";")
        if cookie_name in attributes[0]:
            cookie = {}
            for attr in attributes:
                split = attr.split("=")
                cookie[split[0].strip().lower()] = split[1] if len(split) > 1 else True
            return cookie
    return None