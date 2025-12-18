def test_connect_returns_400_if_no_token(client):
    response = client.post('/connect')
    assert response.status_code == 400
    assert response.json['message'] == 'Token required'

def test_connect_returns_401_with_malformed_token(client, test_user):
    response = client.post('/connect', headers=[['Authorization', 'Bearer BAD_TOKEN']])
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid token'

def test_connect_returns_401_with_bad_token(client, test_user):
    response = client.post('/connect', headers=[['Authorization', 'Bearer $1$BAD_TOKEN']])
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid token'

def test_connect_returns_200_with_good_token(client, test_user_token):
    response = client.post('/connect', headers=[['Authorization', f"Bearer {test_user_token}"]])
    assert response.status_code == 200
    assert response.json['access_token'] is not None
    assert response.json['refresh_token'] is not None
    assert response.json['access_token'] != response.json['refresh_token']

def test_refresh_without_token(client, test_user):
    response = client.post('/refresh')
    assert response.status_code == 401

def test_refresh_with_bad_token(client, test_user):
    response = client.post('/refresh', headers=[['Authorization', 'Bearer BAD_TOKEN']])
    assert response.status_code >= 400
    assert response.status_code < 500

def test_refresh_with_good_token(client, test_user_token):
    response = client.post('/connect', headers=[['Authorization', f"Bearer {test_user_token}"]])
    assert response.status_code == 200
    auth_token = response.json['access_token']
    refresh_token = response.json['refresh_token']
    assert refresh_token is not None

    ## verify the original token works
    response = client.get('/me', headers=[['Authorization', f"Bearer {auth_token}"]])
    assert response.status_code == 200
    
    ## verify refresh
    response = client.post('/refresh', headers=[['Authorization', f"Bearer {refresh_token}"]])
    assert response.status_code == 200
    new_token = response.json['access_token']
    assert new_token is not None
    assert new_token != auth_token

    ## verify the new token works
    response = client.get('/me', headers=[['Authorization', f"Bearer {new_token}"]])
    assert response.status_code == 200
    
def test_protected_with_token(client, user_headers):
    response = client.get('/me', headers=user_headers)

    assert response.status_code == 200
    assert response.json['logged_in_as'] == 'user1'

def test_protected_without_token(client, test_user):
    response = client.get('/me')
    assert response.status_code == 401
