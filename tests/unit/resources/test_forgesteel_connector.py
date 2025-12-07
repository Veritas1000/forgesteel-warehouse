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
    assert response.status_code == 204

def test_protected_with_token(client, csrf_headers):
    response = client.get('/me', headers=csrf_headers)

    assert response.status_code == 200
    assert response.json['logged_in_as'] == 'user1'

def test_protected_without_token(client, test_user):
    response = client.get('/me')
    assert response.status_code == 401
