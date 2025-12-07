from datetime import date
from typing import Any
from unittest.mock import MagicMock, Mock, patch

from flask.testing import FlaskClient
from forgesteel_warehouse.resources.token_handler import TEMP_LOGIN_COOKIE_NAME, TOKEN_COOKIE_NAME, TOKEN_REFRESH_COOKIE_NAME
from forgesteel_warehouse.utils.patreon_api import PatreonApi, PatreonUser, PatronState


def test_session_returns_no_session_when_none(client: FlaskClient, patreon_api: MagicMock):
    response = client.get('/th/session')
    assert response.status_code == 200
    assert response.json is not None
    assert response.json['authenticated_with_patreon'] is False
    assert response.json['user'] is None

def test_session_returns_session_when_present(client: FlaskClient, patreon_api: MagicMock):
    start_date = date(2025, 10, 31)
    mock_user_data = PatreonUser(mcdm=PatronState(patron=True, tier_cents=800, start=start_date))
    patreon_api.get_identity.return_value = mock_user_data

    client.set_cookie(TOKEN_COOKIE_NAME, 'test-cookie')
    response = client.get('/th/session')
    assert response.status_code == 200
    assert response.json is not None
    assert response.json['authenticated_with_patreon'] == True
    assert response.json['user']['mcdm']['patron'] == True
    assert response.json['user']['mcdm']['tier_cents'] == 800
    assert '31 Oct 2025' in response.json['user']['mcdm']['start']

    patreon_api.get_identity.assert_called_with('test-cookie')

def test_login_start_returns_url_and_sets_temp_cookie(client: FlaskClient, patreon_api: MagicMock):
    auth_url = 'https://fake.generated/auth/url'
    patreon_api.generate_authorize_url.return_value = auth_url

    assert client.get_cookie(TEMP_LOGIN_COOKIE_NAME) is None

    response = client.post('/th/login/start')

    args = patreon_api.generate_authorize_url.call_args.args
 
    assert response.status_code == 200
    assert response.json is not None
    assert response.json['authorizationUrl'] == auth_url

    cookie = client.get_cookie(TEMP_LOGIN_COOKIE_NAME)
    assert cookie is not None
    assert cookie.value == args[1]

def test_login_end_fails_on_bad_state(client: FlaskClient, patreon_api: MagicMock):
    login_cookie = 'expected-login-cookie'
    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    
    response = client.post('/th/login/end', json={'state': 'wrong-state', 'code': 'abc123'})

    assert response.status_code == 400
    assert response.json is not None
    assert response.json['message'] == 'Invalid Authorization request'

def test_login_end_success(client: FlaskClient, patreon_api: MagicMock):
    login_cookie = 'expected-login-cookie'
    patreon_code = 'pcode_asdf'

    auth_token = 'qwerty_5432'
    refresh_token = 'refresh_5432'
    lifetime = 5432
    patreon_api.get_token.return_value = auth_token, refresh_token, lifetime
    mock_user_data = PatreonUser(mcdm=PatronState(patron=True, tier_cents=800, start=date(2022, 2, 22)))
    patreon_api.get_identity.return_value = mock_user_data

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post('/th/login/end', json={'state': login_cookie, 'code': patreon_code})

    ## Verify API calls
    patreon_api.get_token.assert_called_with(patreon_code, 'http://some.fake/oauth-redirect')
    patreon_api.get_identity.assert_called_with(auth_token)

    ## Verify response contents
    assert response.status_code == 200
    assert response.json is not None
    assert response.json['authenticated_with_patreon'] == True
    assert response.json['user']['mcdm']['patron'] == True

    ## Verify cookies
    token_cookie = client.get_cookie(TOKEN_COOKIE_NAME)
    assert token_cookie is not None
    assert token_cookie.value == auth_token
    assert token_cookie.max_age == lifetime
    assert token_cookie.http_only == True
    
    refresh_cookie = client.get_cookie(TOKEN_REFRESH_COOKIE_NAME)
    assert refresh_cookie is not None
    assert refresh_cookie.value == refresh_token
    assert refresh_cookie.max_age == lifetime
    assert refresh_cookie.http_only == True
    
    login_cookie = client.get_cookie(TEMP_LOGIN_COOKIE_NAME)
    assert login_cookie is None

def test_login_end_handles_api_errors(client: FlaskClient, patreon_api: MagicMock):
    login_cookie = 'expected-login-cookie'

    patreon_api.get_token.side_effect = Exception('Some API exception')

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post('/th/login/end', json={'state': login_cookie, 'code': 'some_wrong_code'})

    assert response.status_code == 400
    assert response.json is not None
    assert response.json['authenticated_with_patreon'] == False
    assert 'Some API exception' in response.json['message']

def test_refresh_updates_secure_cookies(client: FlaskClient, patreon_api: MagicMock):
    old_refresh_token = 'old_refresh_1234'
    
    auth_token = 'qwerty_5432'
    refresh_token = 'refresh_5432'
    lifetime = 5432
    patreon_api.refresh_token.return_value = auth_token, refresh_token, lifetime
    
    client.set_cookie(TOKEN_REFRESH_COOKIE_NAME, old_refresh_token)
    response = client.post('/th/refresh')

    patreon_api.refresh_token.assert_called_with(old_refresh_token)
    
    ## Verify response contents
    assert response.status_code == 204

    ## Verify cookies
    token_cookie = client.get_cookie(TOKEN_COOKIE_NAME)
    assert token_cookie is not None
    assert token_cookie.value == auth_token
    assert token_cookie.max_age == lifetime
    assert token_cookie.http_only == True
    
    refresh_cookie = client.get_cookie(TOKEN_REFRESH_COOKIE_NAME)
    assert refresh_cookie is not None
    assert refresh_cookie.value == refresh_token
    assert refresh_cookie.max_age == lifetime
    assert refresh_cookie.http_only == True
    
def test_logout_deletes_cookies(client: FlaskClient, patreon_api: MagicMock):
    client.set_cookie(TOKEN_COOKIE_NAME, 'some-token')
    client.set_cookie(TOKEN_REFRESH_COOKIE_NAME, 'refresh-token')
    
    response = client.post('/th/logout')

    assert response.status_code == 204
    assert client.get_cookie(TOKEN_COOKIE_NAME) is None
    assert client.get_cookie(TOKEN_REFRESH_COOKIE_NAME) is None
