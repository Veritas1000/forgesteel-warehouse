import uuid
from datetime import date
from unittest.mock import MagicMock, call

import pytest
from requests import HTTPError

from forgesteel_warehouse import db
from forgesteel_warehouse.models import User
from forgesteel_warehouse.resources.token_handler import TEMP_LOGIN_COOKIE_NAME
from forgesteel_warehouse.utils.patreon_api import PatreonUser, PatronState


def test_login_start_returns_url_and_sets_temp_cookie(client, patreon_api):
    auth_url = "https://fake.generated/auth/url"
    patreon_api.generate_authorize_url.return_value = auth_url

    assert client.get_cookie(TEMP_LOGIN_COOKIE_NAME) is None

    response = client.post("/th/login/start")

    args = patreon_api.generate_authorize_url.call_args.args

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authorizationUrl"] == auth_url

    cookie = client.get_cookie(TEMP_LOGIN_COOKIE_NAME)
    assert cookie is not None
    assert cookie.value == args[1]


def test_login_end_fails_on_bad_state(client, patreon_api):
    login_cookie = "expected-login-cookie"
    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)

    response = client.post(
        "/th/login/end", json={"state": "wrong-state", "code": "abc123"}
    )

    assert response.status_code == 400
    assert response.json is not None
    assert response.json["message"] == "Invalid Authorization request"


def test_login_end_success(client, patreon_api):
    mock_user_data = PatreonUser(
        id="1234",
        mcdm=PatronState(patron=True, tier_cents=800, start=date(2022, 2, 22)),
    )
    lifetime = 5432
    auth_token = "qwerty_5432"
    refresh_token = "refresh_5432"
    patreon_api.get_token.return_value = auth_token, refresh_token, lifetime
    patreon_api.get_identity.return_value = mock_user_data

    login_cookie = "expected-login-cookie"
    patreon_code = "pcode_asdf"

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post(
        "/th/login/end", json={"state": login_cookie, "code": patreon_code}
    )

    ## Verify API calls
    patreon_api.get_token.assert_called_with(
        patreon_code, "http://some.fake/oauth-redirect"
    )
    patreon_api.get_identity.assert_called_with(auth_token)

    ## Verify response contents
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] == True
    assert response.json["user"]["mcdm"]["patron"] == True

    login_cookie = client.get_cookie(TEMP_LOGIN_COOKIE_NAME)
    assert login_cookie is None


def test_login_end_success_creates_user_for_patrons(client, patreon_api):
    user_patreon_id = "12345678"
    user_patreon_email = "test@email.com"
    ## Verify user doesn't exist yet
    user = User.find_by_patreon_id(user_patreon_id)
    assert user is None

    mock_user_data = PatreonUser(
        id=user_patreon_id,
        email=user_patreon_email,
        forgesteel=PatronState(patron=True, start=date(2022, 2, 22)),
    )
    lifetime = 5432
    auth_token = "qwerty_5432"
    refresh_token = "refresh_5432"
    patreon_api.get_token.return_value = auth_token, refresh_token, lifetime
    patreon_api.get_identity.return_value = mock_user_data

    login_cookie = "expected-login-cookie"
    patreon_code = "pcode_asdf"

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post(
        "/th/login/end", json={"state": login_cookie, "code": patreon_code}
    )

    ## Verify response contents
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] == True
    assert response.json["user"]["id"] == user_patreon_id
    assert response.json["user"]["email"] == user_patreon_email
    assert response.json["user"]["forgesteel"]["patron"] == True

    ## Verify User exists
    user = User.find_by_patreon_id(user_patreon_id)
    assert user is not None
    assert user.patreon_id == user_patreon_id
    assert user.patreon_email == user_patreon_email
    assert user.get_patreon_access_token() == auth_token
    assert user.get_patreon_refresh_token() == refresh_token

    ## Session tokens should be created
    token_cookie = client.get_cookie("jwt_access_cookie_name")
    assert token_cookie is not None
    refresh_cookie = client.get_cookie("jwt_refresh_cookie_name")
    assert refresh_cookie is not None
    csrf_cookie = client.get_cookie("jwt_access_csrf_cookie_name")
    assert csrf_cookie is not None

def test_login_end_success_creates_user_for_non_patrons(client, patreon_api):
    user_patreon_id = "87654321"
    user_patreon_email = "test@email.com"
    ## Verify user doesn't exist yet
    user = User.find_by_patreon_id(user_patreon_id)
    assert user is None

    login_cookie = "expected-login-cookie"
    patreon_code = "pcode_asdf"

    auth_token = "qwerty_5432"
    refresh_token = "refresh_5432"
    lifetime = 5432
    patreon_api.get_token.return_value = auth_token, refresh_token, lifetime
    mock_user_data = PatreonUser(
        id=user_patreon_id,
        email=user_patreon_email,
        forgesteel=PatronState(patron=False),
    )
    patreon_api.get_identity.return_value = mock_user_data

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post(
        "/th/login/end", json={"state": login_cookie, "code": patreon_code}
    )

    ## Verify response contents
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] == True
    assert response.json["user"]["id"] == user_patreon_id
    assert response.json["user"]["email"] == user_patreon_email
    assert response.json["user"]["forgesteel"]["patron"] == False

    ## Verify session cookies NOT created for non-patron
    token_cookie = client.get_cookie("jwt_access_cookie_name")
    assert token_cookie is None
    refresh_cookie = client.get_cookie("jwt_refresh_cookie_name")
    assert refresh_cookie is None
    csrf_cookie = client.get_cookie("jwt_access_csrf_cookie_name")
    assert csrf_cookie is None

    ## Verify User exists
    user = User.find_by_patreon_id(user_patreon_id)
    assert user is not None
    assert user.patreon_id == user_patreon_id
    assert user.patreon_email == user_patreon_email
    assert user.get_patreon_access_token() == auth_token
    assert user.get_patreon_refresh_token() == refresh_token


def test_login_end_success_doesnt_recreate_existing_user(client, patreon_api):
    user_patreon_id = "8675309"
    user_patreon_email = "test@email.com"

    existing_user = User(name=user_patreon_email)
    existing_user.patreon_email = user_patreon_email
    existing_user.patreon_id = user_patreon_id
    db.session.add(existing_user)
    db.session.commit()

    ## Verify user exists
    user = User.find_by_patreon_id(user_patreon_id)
    assert user is not None
    assert user.patreon_id == user_patreon_id
    assert user.patreon_email == user_patreon_email

    login_cookie = "expected-login-cookie"
    patreon_code = "pcode_asdf"

    auth_token = "qwerty_5432"
    refresh_token = "refresh_5432"
    lifetime = 5432
    patreon_api.get_token.return_value = auth_token, refresh_token, lifetime
    mock_user_data = PatreonUser(
        id=user_patreon_id,
        email=user_patreon_email,
        forgesteel=PatronState(patron=False),
    )
    patreon_api.get_identity.return_value = mock_user_data

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post(
        "/th/login/end", json={"state": login_cookie, "code": patreon_code}
    )

    ## Verify response contents
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] == True
    assert response.json["user"]["id"] == user_patreon_id
    assert response.json["user"]["email"] == user_patreon_email
    assert response.json["user"]["forgesteel"]["patron"] == False

    ## Verify User still there
    user = User.find_by_patreon_id(user_patreon_id)
    assert user is not None
    assert user.patreon_id == user_patreon_id
    assert user.patreon_email == user_patreon_email
    ## Should still set Patreon tokens
    assert user.get_patreon_access_token() == auth_token
    assert user.get_patreon_refresh_token() == refresh_token


def test_login_end_handles_api_errors(client, patreon_api):
    login_cookie = "expected-login-cookie"

    patreon_api.get_token.side_effect = Exception("Some API exception")

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post(
        "/th/login/end", json={"state": login_cookie, "code": "some_wrong_code"}
    )

    assert response.status_code == 400
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] == False
    assert "Some API exception" in response.json["message"]


@pytest.fixture()
def test_patreon_user_id():
    return uuid.uuid4().hex


@pytest.fixture()
def authenticated_client(client, test_patreon_user_id, patreon_api):
    user_patreon_email = "test@email.com"
    ## Verify user doesn't exist yet
    user = User.find_by_patreon_id(test_patreon_user_id)
    assert user is None

    login_cookie = "expected-login-cookie"
    patreon_code = "pcode_asdf"

    auth_token = "qwerty_5432"
    refresh_token = "refresh_5432"
    lifetime = 5432
    patreon_api.get_token.return_value = auth_token, refresh_token, lifetime
    mock_user_data = PatreonUser(
        id=test_patreon_user_id,
        email=user_patreon_email,
        forgesteel=PatronState(patron=True),
    )
    patreon_api.get_identity.return_value = mock_user_data

    client.set_cookie(TEMP_LOGIN_COOKIE_NAME, login_cookie)
    response = client.post(
        "/th/login/end", json={"state": login_cookie, "code": patreon_code}
    )

    ## Verify csrf cookie is set
    csrf_cookie = client.get_cookie("jwt_access_csrf_cookie_name")
    assert csrf_cookie is not None

    ## Verify Patreon tokens set
    user = User.find_by_patreon_id(test_patreon_user_id)
    assert user is not None
    assert user.get_patreon_access_token() == auth_token
    assert user.get_patreon_refresh_token() == refresh_token

    yield client


def test_refresh_updates_secure_cookies(
    authenticated_client, test_patreon_user_id, patreon_api
):
    new_auth_token = "new_auth_1234"
    new_refresh_token = "new_refresh_1234"
    patreon_api.refresh_token.return_value = new_auth_token, new_refresh_token, 600

    csrf_cookie = authenticated_client.get_cookie("jwt_access_csrf_cookie_name")
    csrf = csrf_cookie.value
    response = authenticated_client.post("/th/refresh", headers={"X-CSRF-TOKEN": csrf})

    assert response.status_code == 204

    ## Verify tokens updated
    user = User.find_by_patreon_id(test_patreon_user_id)
    assert user is not None
    assert user.get_patreon_access_token() == new_auth_token
    assert user.get_patreon_refresh_token() == new_refresh_token


def test_logout_deletes_tokens(authenticated_client, test_patreon_user_id, patreon_api):
    csrf_cookie = authenticated_client.get_cookie("jwt_access_csrf_cookie_name")
    csrf = csrf_cookie.value
    response = authenticated_client.post("/th/logout", headers={"X-CSRF-TOKEN": csrf})

    assert response.status_code == 204

    ## Verify User Patreon tokens are gone
    user = User.find_by_patreon_id(test_patreon_user_id)
    assert user is not None
    assert user.get_patreon_access_token() == None
    assert user.get_patreon_refresh_token() == None


def test_session_returns_no_session_when_none(client, patreon_api):
    response = client.get("/th/session")

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] is False
    assert response.json["user"] is None


def test_session_returns_session_when_present(authenticated_client, patreon_api):
    start_date = date(2025, 10, 31)
    mock_user_data = PatreonUser(
        mcdm=PatronState(patron=True, tier_cents=800, start=start_date)
    )
    patreon_api.get_identity.return_value = mock_user_data

    csrf_cookie = authenticated_client.get_cookie("jwt_access_csrf_cookie_name")
    csrf = csrf_cookie.value
    response = authenticated_client.get("/th/session", headers={"X-CSRF-TOKEN": csrf})

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] == True
    assert response.json["user"]["mcdm"]["patron"] == True
    assert response.json["user"]["mcdm"]["tier_cents"] == 800
    assert "31 Oct 2025" in response.json["user"]["mcdm"]["start"]


def test_session_retries_on_401(authenticated_client, test_patreon_user_id, patreon_api):
    user = User.find_by_patreon_id(test_patreon_user_id)
    assert user is not None
    user.set_patreon_access_token("old_auth")
    user.set_patreon_refresh_token("refresh_token_1")
    db.session.commit()

    start_date = date(2025, 10, 31)
    mock_user_data = PatreonUser(
        id=test_patreon_user_id,
        mcdm=PatronState(
            patron=True,
            tier_cents=800,
            start=start_date
        )
    )

    unauth_response = MagicMock()
    unauth_response.status_code = 401
    patreon_api.get_identity.side_effect = (
        HTTPError("Unauthorized", response=unauth_response),
        mock_user_data,
    )

    patreon_api.refresh_token.return_value = "new_auth_token", "new_refresh_token", 100

    response = authenticated_client.get("/th/session")

    assert response.status_code == 200
    assert response.json is not None
    assert response.json["authenticated_with_patreon"] == True
    assert response.json["user"]["mcdm"]["patron"] == True
    assert response.json["user"]["mcdm"]["tier_cents"] == 800
    assert "31 Oct 2025" in response.json["user"]["mcdm"]["start"]

    patreon_api.get_identity.assert_has_calls(
        [
            call("old_auth"),
            call("new_auth_token")
        ]
    )
    patreon_api.refresh_token.assert_called_with("refresh_token_1")

    ## Check user
    user = User.find_by_patreon_id(test_patreon_user_id)
    assert user is not None
    assert user.get_patreon_access_token() == "new_auth_token"
    assert user.get_patreon_refresh_token() == "new_refresh_token"
