import os
from unittest import mock
from flask import Flask
import pytest

from flask_migrate import upgrade
from forgesteel_warehouse import init_app, db
from forgesteel_warehouse.api_key import ApiKey
from forgesteel_warehouse.models import User

@pytest.fixture(scope="session")
def app():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
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
    authResponse = app.test_client().get('/connect', headers=[['Authorization', f"Bearer {test_user_token}"]])
    token = authResponse.json['access_token'] if authResponse.json is not None else ''
    return token

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            'PATREON_CLIENT_ID': 'FAKE_PATREON_CLIENT_ID',
            'PATREON_CLIENT_SECRET': 'FAKE_PATREON_CLIENT_SECRET',
            'PATREON_OAUTH_REDIRECT_URI': 'http://some.fake/oauth-redirect',
            'PATREON_CAMPAIGN_ID_MCDM': 'abcd-88c1-4bdf-b7b5-1234',
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield
