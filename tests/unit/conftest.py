import os
from typing import Dict
from unittest import mock

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_migrate import upgrade
from sqlalchemy import delete

from forgesteel_warehouse import db, init_app
from forgesteel_warehouse.api_key import ApiKey
from forgesteel_warehouse.models import FsHero, FsHomebrew, User


@pytest.fixture(scope="session")
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_ACCESS_COOKIE_NAME": "jwt_access_cookie_name",
        "JWT_REFRESH_COOKIE_NAME": "jwt_refresh_cookie_name",
        "JWT_ACCESS_CSRF_COOKIE_NAME": "jwt_access_csrf_cookie_name",
        "JWT_COOKIE_DOMAIN": None,
    }
    app = init_app(test_config)

    with app.app_context():
        upgrade()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def clean_data_client(client):
    db.session.execute(delete(FsHomebrew))
    db.session.execute(delete(FsHero))
    db.session.commit()
    yield client
    db.session.execute(delete(FsHomebrew))
    db.session.execute(delete(FsHero))
    db.session.commit()


@pytest.fixture(scope="session")
def test_user(app: Flask):
    with app.app_context():
        auth_key = 'TOKEN-1'
        user1 = User(name='user1', auth_key=auth_key)
        db.session.add(user1)
        db.session.commit()
        
        yield user1

        db.session.delete(user1)

@pytest.fixture(scope="session")
def test_user_token(test_user: User):
    return ApiKey.makeApiKey(test_user.id, 'TOKEN-1')

@pytest.fixture(scope="session")
def auth_token(app: Flask, test_user_token: str):
    authResponse = app.test_client().post('/connect', headers=[['Authorization', f"Bearer {test_user_token}"]])
    token = authResponse.json['access_token'] if authResponse.json is not None else ''
    return token

@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return [['Authorization', f"Bearer {auth_token}"]]

@pytest.fixture()
def csrf_headers(client: FlaskClient, test_user_token: str):
    response = client.post('/connect', headers=[['Authorization', f"Bearer {test_user_token}"]])
    
    token = get_csrf_access_token_from_response(response)
    
    return {"X-CSRF-TOKEN": token}

@pytest.fixture(params=['csrf_headers', 'auth_headers'])
def user_headers(request):
    return request.getfixturevalue(request.param)

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch: pytest.MonkeyPatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            "PATREON_CLIENT_ID": "FAKE_PATREON_CLIENT_ID",
            "PATREON_CLIENT_SECRET": "FAKE_PATREON_CLIENT_SECRET",
            "PATREON_OAUTH_REDIRECT_URI": "http://some.fake/oauth-redirect",
            "PATREON_CAMPAIGN_ID_FORGESTEEL": "12345678",
            "PATREON_CAMPAIGN_ID_MCDM": "42424242",
            "JWT_COOKIE_DOMAIN": "",
            "LOG_LEVEL": "",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield

def get_csrf_access_token_from_response(response):
    csrf_cookie = get_cookie_from_response(response, "jwt_access_csrf_cookie_name")
    token = (
        csrf_cookie["jwt_access_csrf_cookie_name"] if csrf_cookie is not None else None
    )
    return token

def get_cookie_from_response(response, cookie_name) -> Dict[str, str] | None:
    cookie_headers = response.headers.getlist("Set-Cookie")
    for header in cookie_headers:
        attributes = header.split(";")
        if cookie_name in attributes[0]:
            cookie = {}
            for attr in attributes:
                split = attr.split("=")
                cookie[split[0].strip().lower()] = split[1] if len(split) > 1 else True
            return cookie
    return None
