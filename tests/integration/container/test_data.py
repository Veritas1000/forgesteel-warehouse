import pytest


@pytest.fixture(params=[
    'forgesteel-heroes',
    'forgesteel-homebrew-settings',
    'forgesteel-session',
    'forgesteel-hidden-setting-ids'
    ])
def data_key_endpoint(container_url, request):
    return f"{container_url}/data/{request.param}"

def test_get_data_with_token_returns_data(requests_session, user_headers, data_key_endpoint):
    response = requests_session.get(data_key_endpoint, headers=user_headers)

    assert response.status_code == 200
    assert response.json() is not None
    assert 'data' in response.json()

def test_put_data_key_with_token_succeeds(requests_session, user_headers, data_key_endpoint):
    response = requests_session.put(data_key_endpoint,
                                    json={'foo': 'bar'},
                                    headers=user_headers)
    assert response.ok

def test_put_data_key_returns_same_with_get(requests_session, user_headers, data_key_endpoint):
    data = [{'foo': 'bar'}]
    response1 = requests_session.put(data_key_endpoint,
                          json=data,
                          headers=user_headers)

    assert response1.ok

    response2 = requests_session.get(data_key_endpoint, headers=user_headers)

    assert response2.ok
    assert response2.json()['data'] == data

def test_put_data_key_updates_existing(requests_session, user_headers, data_key_endpoint):
    data1 = [{'foo': 'bar'}]
    response1 = requests_session.put(data_key_endpoint,
                          json=data1,
                          headers=user_headers)

    assert response1.ok

    data2 = [{'foo': 'baz'}, {'bar': 'foo2'}]
    response2 = requests_session.put(data_key_endpoint,
                          json=data2,
                          headers=user_headers)

    assert response2.ok

    response3 = requests_session.get(data_key_endpoint, headers=user_headers)

    assert response3.ok
    assert response3.json()['data'] == data2

