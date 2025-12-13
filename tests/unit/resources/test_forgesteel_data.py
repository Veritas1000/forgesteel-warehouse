import pytest


def test_get_data_without_token_returns_401(client, test_user):
    response = client.get('/data')
    assert response.status_code == 401

@pytest.mark.parametrize('headers', [('csrf_headers'), ('auth_headers')])
def test_get_data_with_token_returns_keys(headers, client, request):
    response = client.get('/data', headers=request.getfixturevalue(headers))

    assert response.status_code == 200
    assert response.json['keys'] is not None
    assert 'forgesteel-heroes' in response.json['keys']
    assert 'forgesteel-homebrew-settings' in response.json['keys']
    assert 'forgesteel-session' in response.json['keys']
    assert 'forgesteel-hidden-setting-ids' in response.json['keys']

def test_get_data_sub_without_token_returns_401(client, test_user):
    response = client.get('/data/anything-here')
    assert response.status_code == 401

def test_get_bad_data_key_returns_404(client, csrf_headers):
    response = client.get('/data/bad-key', headers=csrf_headers)
    assert response.status_code == 404

def test_put_data_sub_without_token_returns_401(client, test_user):
    response = client.put('/data/anything-here', 
                          json={'foo': 'bar'})
    assert response.status_code == 401

def test_put_bad_data_key_returns_404(client, csrf_headers):
    response = client.put('/data/bad-key',
                          json={'foo': 'bar'},
                          headers=csrf_headers)
    assert response.status_code == 404
