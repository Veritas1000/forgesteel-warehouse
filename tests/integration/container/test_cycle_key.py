import re
import requests

from tests.utils import get_csrf_access_token_from_response


def test_cycle_user_key(app_container, api_token):
    ## Verify initial connectivity
    url = app_container._create_connection_url()
    connect_headers = {'Authorization': f"Bearer {api_token}"}
    cr = requests.get(f"{url}/connect", headers=connect_headers)
    
    token = get_csrf_access_token_from_response(cr)
    assert cr.status_code == 204
    assert token is not None

    ## generate a new key
    exit_code, output = app_container.exec('python /app/utils/cycle_key.py')
    log = output.decode() if output else ""
    token_match = re.search(r"^(\$[0-9]+\$[0-9a-f]+)$", log, re.MULTILINE)
    new_token = token_match.group(1) if token_match is not None else None

    assert new_token is not None
    assert new_token != api_token
    assert new_token[0:3] == api_token[0:3]

    ## Verify old token no longer works
    cr = requests.get(f"{url}/connect", headers=connect_headers)

    assert cr.status_code == 401

    ## verify new token
    new_connect_headers = {'Authorization': f"Bearer {new_token}"}
    cr = requests.get(f"{url}/connect", headers=new_connect_headers)
    access_token = cr.json()['access_token']
    
    assert cr.status_code == 200
    assert access_token is not None
