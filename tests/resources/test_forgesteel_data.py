def test_get_data_without_token_returns_401(client, test_user):
    response = client.get('/data')
    assert response.status_code == 401

def test_get_data_with_token_returns_keys(client, auth_token):
    response = client.get('/data', headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response.status_code == 200
    assert response.json['keys'] is not None
    assert 'forgesteel-heroes' in response.json['keys']

def test_get_data_sub_without_token_returns_401(client, test_user):
    response = client.get('/data/anything-here')
    assert response.status_code == 401

def test_get_bad_data_key_returns_404(client, auth_token):
    response = client.get('/data/bad-key', headers=[['Authorization', f"Bearer {auth_token}"]])
    assert response.status_code == 404

def test_get_heroes_with_token_returns_data(client, auth_token):
    response = client.get('/data/forgesteel-heroes', headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response.status_code == 200
    assert response.json is not None
    assert 'data' in response.json

def test_put_data_sub_without_token_returns_401(client, test_user):
    response = client.put('/data/anything-here', 
                          json={'foo': 'bar'})
    assert response.status_code == 401

def test_put_bad_data_key_returns_404(client, auth_token):
    response = client.put('/data/bad-key',
                          json={'foo': 'bar'},
                          headers=[['Authorization', f"Bearer {auth_token}"]])
    assert response.status_code == 404

def test_put_heroes_with_token_returns_data(client, auth_token):
    response = client.put('/data/forgesteel-heroes',
                          json={'foo': 'bar'},
                          headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response.status_code == 204

def test_put_heroes_returns_same_with_get(client, auth_token):
    data = [{'foo': 'bar'}]
    response1 = client.put('/data/forgesteel-heroes',
                          json=data,
                          headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response1.status_code == 204

    response2 = client.get('/data/forgesteel-heroes', headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response2.status_code == 200
    assert response2.json['data'] == data

def test_put_heroes_updates_existing(client, auth_token):
    data1 = [{'foo': 'bar'}]
    response1 = client.put('/data/forgesteel-heroes',
                          json=data1,
                          headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response1.status_code == 204

    data2 = [{'foo': 'baz'}, {'bar': 'foo2'}]
    response2 = client.put('/data/forgesteel-heroes',
                          json=data2,
                          headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response2.status_code == 204

    response3 = client.get('/data/forgesteel-heroes', headers=[['Authorization', f"Bearer {auth_token}"]])

    assert response3.status_code == 200
    assert response3.json['data'] == data2
