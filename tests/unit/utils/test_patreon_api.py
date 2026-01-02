from datetime import date
import json
import os
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
from requests import HTTPError
from forgesteel_warehouse.utils.patreon_api import PatreonApi


def test_constructor_reads_env_vars():
    api = PatreonApi()
    assert api.CLIENT_ID == 'FAKE_PATREON_CLIENT_ID'
    assert api.CLIENT_SECRET == 'FAKE_PATREON_CLIENT_SECRET'

def test_generate_authorize_url():
    api = PatreonApi()
    redirect = 'http://some.redirect:8080/uri/#/with/hash'
    state = 'fakeState'
    url = api.generate_authorize_url(redirect, state)
    parsed = urlparse(url)

    assert '#' not in url, "URL isn't properly escaping unsafe URL chars!"
    
    assert parsed.scheme == 'https'
    assert parsed.netloc == 'www.patreon.com'
    assert parsed.path == '/oauth2/authorize'
    query_params = parse_qs(parsed.query)
    assert query_params['response_type'] == ['code']
    assert query_params['client_id'] == ['FAKE_PATREON_CLIENT_ID']
    assert query_params['redirect_uri'] == [redirect]
    assert query_params['scope'] == [' '.join(api._requested_token_scopes)]
    assert query_params['state'] == [state]

@patch('requests.post')
def test_get_token_success(mock_post):
    mock_token = 'abc_123_fake'
    mock_refresh = 'abc_123_fake_refresh'
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'access_token': mock_token,
        'refresh_token': mock_refresh,
        'expires_in': 1234,
        'scope': 'foo',
        'token_type': 'Bearer'
    }

    api = PatreonApi()
    code = 'a_fake_code'
    redirect = 'http://some.redirect:8080/uri/#/with/hash'
    token, refresh, lifetime = api.get_token(code, redirect)

    call_params = mock_post.call_args.kwargs['params']
    assert call_params is not None
    assert call_params['grant_type'] == 'authorization_code'
    assert call_params['code'] == code
    assert call_params['redirect_uri'] == redirect
    assert call_params['client_id'] == 'FAKE_PATREON_CLIENT_ID'
    assert call_params['client_secret'] == 'FAKE_PATREON_CLIENT_SECRET'
    
    assert token == mock_token
    assert refresh == mock_refresh
    assert lifetime == 1234

@patch('requests.post')
def test_get_token_code_error(mock_post):
    mock_response = mock_post.return_value
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "error": "invalid_grant",
        "error_description": "Invalid 'code' in request."
    }
    mock_response.raise_for_status.side_effect = HTTPError('Error from patreon')

    api = PatreonApi()
    code = 'a_bad_code'
    redirect = 'http://some.redirect:8080/uri/#/with/hash'
    with pytest.raises(HTTPError, match="Error from patreon"):
        api.get_token(code, redirect)

@patch('requests.post')
def test_get_token_other_error(mock_post):
    mock_response = mock_post.return_value
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError('Error from patreon')

    api = PatreonApi()
    code = 'a_bad_code'
    redirect = 'http://some.redirect:8080/uri/#/with/hash'
    with pytest.raises(HTTPError, match="Error from patreon"):
        api.get_token(code, redirect)

@patch('requests.post')
def test_refresh_token_success(mock_post):
    old_refresh_token = 'qwerty_9876'

    new_token = 'abc_123_fake'
    new_refresh = 'abc_123_fake_refresh'
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'access_token': new_token,
        'refresh_token': new_refresh,
        'expires_in': 1234,
        'scope': 'foo',
        'token_type': 'Bearer'
    }

    api = PatreonApi()
    token, refresh, lifetime = api.refresh_token(old_refresh_token)

    call_params = mock_post.call_args.kwargs['params']
    assert call_params is not None
    assert call_params['grant_type'] == 'refresh_token'
    assert call_params['refresh_token'] == old_refresh_token
    assert call_params['client_id'] == 'FAKE_PATREON_CLIENT_ID'
    assert call_params['client_secret'] == 'FAKE_PATREON_CLIENT_SECRET'
    
    assert token == new_token
    assert refresh == new_refresh
    assert lifetime == 1234

@patch('requests.post')
def test_refresh_token_code_error(mock_post):
    mock_response = mock_post.return_value
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "error": "invalid_grant",
        "error_description": "Invalid 'code' in request."
    }
    mock_response.raise_for_status.side_effect = HTTPError('Error from patreon')

    api = PatreonApi()
    with pytest.raises(HTTPError, match="Error from patreon"):
        api.refresh_token('qwerty_9876')

@patch('requests.post')
def test_refresh_token_other_error(mock_post):
    mock_response = mock_post.return_value
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError('Error from patreon')

    api = PatreonApi()
    with pytest.raises(HTTPError, match="Error from patreon"):
        api.refresh_token('qwerty_9876')

def test__parse_identity_response_mcdm_patron():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data/identity_mcdm_patron.json')) as f:
        mock_data = json.load(f)

        api = PatreonApi()
        user = api._parse_identity_response(mock_data)
        assert user.id == '123456'
        assert user.email == 'test@email.com'
        assert user.mcdm is not None
        assert user.mcdm.patron == True
        assert len(user.mcdm.tiers) == 1
        assert user.mcdm.tiers[0].title == 'MCDM+'
        assert user.mcdm.tier_cents == 800
        assert user.mcdm.start == date(2019, 2, 13)

def test__parse_identity_response_forgesteel_former_patron():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data/identity_forgesteel_former_patron.json')) as f:
        mock_data = json.load(f)

        api = PatreonApi()
        user = api._parse_identity_response(mock_data)
        assert user.id == '123456'
        assert user.email == 'test@email.com'
        assert user.forgesteel is not None
        assert user.forgesteel.patron == False
        assert user.forgesteel.tiers == []
        assert user.forgesteel.tier_cents == 0
        assert user.forgesteel.start == None

def test__parse_identity_response_mcdm_former_patron():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data/identity_mcdm_former_patron.json')) as f:
        mock_data = json.load(f)

        api = PatreonApi()
        user = api._parse_identity_response(mock_data)
        assert user.id == '123456'
        assert user.email == 'test@email.com'
        assert user.mcdm is not None
        assert user.mcdm.patron == False
        assert user.mcdm.tiers == []
        assert user.mcdm.tier_cents == 0
        assert user.mcdm.start == None

def test__parse_identity_response_forgesteel_non_patron():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data/identity_forgesteel_non_patron.json')) as f:
        mock_data = json.load(f)

        api = PatreonApi()
        user = api._parse_identity_response(mock_data)
        assert user.id == '123456'
        assert user.email == 'test@email.com'
        assert user.forgesteel is not None
        assert user.forgesteel.patron == False
        assert user.forgesteel.tiers == []
        assert user.forgesteel.tier_cents == 0
        assert user.forgesteel.start == None

def test__parse_identity_response_mcdm_non_patron():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data/identity_mcdm_non_patron.json')) as f:
        mock_data = json.load(f)

        api = PatreonApi()
        user = api._parse_identity_response(mock_data)
        assert user.id == '123456'
        assert user.email == 'test@email.com'
        assert user.mcdm is not None
        assert user.mcdm.patron == False
        assert user.mcdm.tiers == []
        assert user.mcdm.tier_cents == 0
        assert user.mcdm.start == None

def test__parse_identity_response_patron_none():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data/identity_none_patron.json')) as f:
        mock_data = json.load(f)

        api = PatreonApi()
        user = api._parse_identity_response(mock_data)
        assert user.id == '123456'
        assert user.email == 'test@email.com'
        assert user.mcdm is not None
        assert user.mcdm.patron == False
        assert user.mcdm.tiers == []
        assert user.mcdm.tier_cents == 0
        assert user.mcdm.start == None
        
        assert user.forgesteel is not None
        assert user.forgesteel.patron == False
        assert user.forgesteel.tiers == []
        assert user.forgesteel.tier_cents == 0
        assert user.forgesteel.start == None

def test__parse_identity_response_no_json():
    mock_data = {}

    api = PatreonApi()
    user = api._parse_identity_response(mock_data)
    assert user.id == None
    assert user.email == None
    assert user.mcdm is not None
    assert user.mcdm.patron == False
    assert user.mcdm.tiers == []
    assert user.mcdm.tier_cents == 0
    assert user.mcdm.start == None
        
    assert user.forgesteel is not None
    assert user.forgesteel.patron == False
    assert user.forgesteel.tiers == []
    assert user.forgesteel.tier_cents == 0
    assert user.forgesteel.start == None

@patch('requests.get')
def test_get_identity_success_patron(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200

    with open(os.path.join(os.path.dirname(__file__), 'mock_data/identity_mcdm_patron.json')) as f:
        mock_data = json.load(f)

    mock_response.json.return_value = mock_data

    token = 'accessToken123'
    api = PatreonApi()
    user_data = api.get_identity(token)

    assert user_data.mcdm is not None
    assert user_data.mcdm.patron == True
    assert user_data.mcdm.tier_cents == 800
    assert user_data.mcdm.start == date(2019, 2, 13)

    mock_get.assert_called_once()


@patch('requests.get')
def test_get_identity_error(mock_get):
    mock_response = mock_get.return_value
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError('Error from patreon')

    token = 'accessToken123'
    api = PatreonApi()
    with pytest.raises(HTTPError, match="Error from patreon"):
        api.get_identity(token)
