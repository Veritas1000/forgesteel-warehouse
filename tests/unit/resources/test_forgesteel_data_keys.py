import pytest

@pytest.fixture(params=[
    'forgesteel-heroes',
    'forgesteel-homebrew-settings',
    'forgesteel-session',
    'forgesteel-hidden-setting-ids'
    ])
def data_key_endpoint(request):
    return f"/data/{request.param}"

def test_get_data_key_with_token_returns_data(client, user_headers, data_key_endpoint):
    response = client.get(data_key_endpoint, headers=user_headers)

    assert response.status_code == 200
    assert response.json is not None
    assert 'data' in response.json

def test_put_data_key_with_token_succeeds(client, user_headers, data_key_endpoint):
    response = client.put(data_key_endpoint,
                          json={'foo': 'bar'},
                          headers=user_headers)

    assert response.status_code == 204

def test_put_data_key_returns_same_with_get(client, user_headers, data_key_endpoint):
    data = [{'foo': 'bar'}]
    response1 = client.put(data_key_endpoint,
                          json=data,
                          headers=user_headers)

    assert response1.status_code == 204

    response2 = client.get(data_key_endpoint, headers=user_headers)

    assert response2.status_code == 200
    assert response2.json['data'] == data

def test_put_data_key_updates_existing(client, user_headers, data_key_endpoint):
    data1 = [{'foo': 'bar'}]
    response1 = client.put(data_key_endpoint,
                          json=data1,
                          headers=user_headers)

    assert response1.status_code == 204

    data2 = [{'foo': 'baz'}, {'bar': 'foo2'}]
    response2 = client.put(data_key_endpoint,
                          json=data2,
                          headers=user_headers)

    assert response2.status_code == 204

    response3 = client.get(data_key_endpoint, headers=user_headers)

    assert response3.status_code == 200
    assert response3.json['data'] == data2
