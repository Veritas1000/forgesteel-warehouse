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

def test_refresh_token(container_url, api_token):
    connect_headers = {'Authorization': f"Bearer {api_token}"}
    cr = requests.post(f"{container_url}/connect", headers=connect_headers)

    access_token = cr.json()['access_token']
    refresh_token = cr.json()['refresh_token']
    assert cr.status_code == 200
    assert access_token is not None
    assert refresh_token is not None

    ## Verify initial token
    cr = requests.get(f"{container_url}/data", headers={'Authorization': f"Bearer {access_token}"})
    assert cr.status_code == 200

    ## Refresh the token
    cr = requests.post(f"{container_url}/refresh", headers={'Authorization': f"Bearer {refresh_token}"})
    assert cr.status_code == 200
    new_token = cr.json()['access_token']
    assert new_token is not None
    
    ## Verify new token
    cr = requests.get(f"{container_url}/data", headers={'Authorization': f"Bearer {new_token}"})
    assert cr.status_code == 200

