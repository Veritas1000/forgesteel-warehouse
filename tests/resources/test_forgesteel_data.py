def test_get_data_without_token_returns_401(client, test_user):
    response = client.get('/data')
    assert response.status_code == 401

def test_get_data_with_token_returns_keys(client, auth_token):
    response = client.get('/data', headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response.status_code == 200
    assert response.json['keys'] is not None
    assert 'forgesteel-heroes' in response.json['keys']
    assert 'forgesteel-homebrew-settings' in response.json['keys']

def test_get_data_sub_without_token_returns_401(client, test_user):
    response = client.get('/data/anything-here')
    assert response.status_code == 401

def test_get_bad_data_key_returns_404(client, auth_token):
    response = client.get('/data/bad-key', headers=[['Authorization', f"Bearer {auth_token}"]])
    assert response.status_code == 404

def test_put_data_sub_without_token_returns_401(client, test_user):
    response = client.put('/data/anything-here', 
                          json={'foo': 'bar'})
    assert response.status_code == 401

def test_put_bad_data_key_returns_404(client, auth_token):
    response = client.put('/data/bad-key',
                          json={'foo': 'bar'},
                          headers=[['Authorization', f"Bearer {auth_token}"]])
    assert response.status_code == 404
