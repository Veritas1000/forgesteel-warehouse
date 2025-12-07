import re

import requests

from tests.integration.utils import get_csrf_headers, get_csrf_token

def test_add_user_script(app_container):
    exit_code, output = app_container.exec('python utils/add_user.py')

    assert exit_code == 0

    log = output.decode() if output else ""

    assert re.search(r"^USER CREATED$", log, re.MULTILINE), "'USER CREATED' not found in logs"
    assert re.search(r"Here is your API KEY", log, re.MULTILINE), "api key instructions not found in logs"
    assert re.search(r"^\$2\$[0-9a-f]+$", log, re.MULTILINE), "api key not found in logs"

def test_user_data_separation(app_container):
    user1_data = [ { 'foo': 'bar' } ]
    user2_data = [ { 'bar': 'baz' }, { 'forge': 'steel' } ]

    ## Insert some data for the default user
    with (requests.Session() as session1, requests.Session() as session2):
        headers = get_csrf_headers(app_container, session1)
        url = app_container._create_connection_url()

        add_req = session1.put(f"{url}/data/forgesteel-homebrew-settings", json=user1_data, headers=headers)
        assert add_req.status_code == 204

        ## Add a new user
        exit_code, output = app_container.exec('python utils/add_user.py')
        log = output.decode() if output else ""
        token_match = re.search(r"^(\$[0-9]+\$[0-9a-f]+)$", log, re.MULTILINE)
        new_token = token_match.group(1) if token_match is not None else None

        assert new_token is not None

        ## Verify the new user has no data
        csrf_token2 = get_csrf_token(app_container, new_token, session2)
        headers2 = {'X-CSRF-TOKEN': csrf_token2}
        get_req = session2.get(f"{url}/data/forgesteel-homebrew-settings", headers=headers2)
        assert get_req.status_code == 200
        assert get_req.json()['data'] == None

        ## insert some data
        add_req = session2.put(f"{url}/data/forgesteel-homebrew-settings", json=user2_data, headers=headers2)
        assert add_req.status_code == 204

        ## Verify data for each user
        get_req1 = session1.get(f"{url}/data/forgesteel-homebrew-settings", headers=headers)
        assert get_req1.status_code == 200
        assert get_req1.json()['data'] == user1_data

        get_req2 = session2.get(f"{url}/data/forgesteel-homebrew-settings", headers=headers2)
        assert get_req2.status_code == 200
        assert get_req2.json()['data'] == user2_data

