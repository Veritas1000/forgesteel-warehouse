def test_connect_returns_400_if_no_token(client):
    response = client.get('/connect')
    assert response.status_code == 400
    assert response.json['message'] == 'Token required'

def test_connect_returns_401_with_bad_token(client, load_test_users):
    response = client.get('/connect', headers=[['Authorization', 'Bearer BAD_TOKEN']])
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid token'

def test_connect_returns_200_with_good_token(client, load_test_users):
    response = client.get('/connect', headers=[['Authorization', 'Bearer TOKEN-1']])
    assert response.status_code == 200
    assert response.json['access_token'] is not None

def test_protected_with_token(client, load_test_users):
    authResponse = client.get('/connect', headers=[['Authorization', 'Bearer TOKEN-1']])
    token = authResponse.json['access_token']

    response = client.get('/me', headers=[['Authorization', f"Bearer {token}"]])

    assert response.status_code == 200
    assert response.json['logged_in_as'] == 'user1'

def test_protected_without_token(client, load_test_users):
    response = client.get('/me')
    assert response.status_code == 401
