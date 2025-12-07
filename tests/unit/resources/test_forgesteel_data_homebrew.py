def test_get_homebrew_with_token_returns_data(client, csrf_headers):
    response = client.get('/data/forgesteel-homebrew-settings', headers=csrf_headers)

    assert response.status_code == 200
    assert response.json is not None
    assert 'data' in response.json

def test_put_homebrew_with_token_returns_data(client, csrf_headers):
    response = client.put('/data/forgesteel-homebrew-settings',
                          json={'foo': 'bar'},
                          headers=csrf_headers)

    assert response.status_code == 204

def test_put_homebrew_returns_same_with_get(client, csrf_headers):
    data = [{'foo': 'bar'}]
    response1 = client.put('/data/forgesteel-homebrew-settings',
                          json=data,
                          headers=csrf_headers)

    assert response1.status_code == 204

    response2 = client.get('/data/forgesteel-homebrew-settings', headers=csrf_headers)

    assert response2.status_code == 200
    assert response2.json['data'] == data

def test_put_homebrew_updates_existing(client, csrf_headers):
    data1 = [{'foo': 'bar'}]
    response1 = client.put('/data/forgesteel-homebrew-settings',
                          json=data1,
                          headers=csrf_headers)

    assert response1.status_code == 204

    data2 = [{'foo': 'baz'}, {'bar': 'foo2'}]
    response2 = client.put('/data/forgesteel-homebrew-settings',
                          json=data2,
                          headers=csrf_headers)

    assert response2.status_code == 204

    response3 = client.get('/data/forgesteel-homebrew-settings', headers=csrf_headers)

    assert response3.status_code == 200
    assert response3.json['data'] == data2
