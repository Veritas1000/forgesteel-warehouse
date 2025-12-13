import requests

def test_auth_required_data(app_container):
    url = app_container._create_connection_url()
    r = requests.get(f"{url}/data")

    assert r.status_code == 401

def test_auth_required_connect(app_container):
    url = app_container._create_connection_url()
    r = requests.post(f"{url}/connect")

    assert r.status_code == 400

def test_connect(container_url, requests_session, user_headers):
    cr = requests_session.get(f"{container_url}/data", headers=user_headers)

    assert cr.status_code == 200
