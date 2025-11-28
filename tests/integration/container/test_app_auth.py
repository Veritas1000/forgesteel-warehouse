import requests

def test_auth_required_data(app_container):
    url = app_container._create_connection_url()
    r = requests.get(f"{url}/data")

    assert r.status_code == 401

def test_auth_required_connect(app_container):
    url = app_container._create_connection_url()
    r = requests.get(f"{url}/connect")

    assert r.status_code == 400

def test_connect(app_container, api_token):
    url = app_container._create_connection_url()

    connect_headers = {'Authorization': f"Bearer {api_token}"}
    cr = requests.get(f"{url}/connect", headers=connect_headers)

    access_token = cr.json()['access_token']
    assert cr.status_code == 200
    assert access_token is not None

    headers = {'Authorization': f"Bearer {access_token}"}
    cr = requests.get(f"{url}/data", headers=headers)

    assert cr.status_code == 200
