import pytest

from forgesteel_warehouse import init_app, db
from forgesteel_warehouse.models import User
from forgesteel_warehouse.api_key import ApiKey

@pytest.fixture(scope="session")
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    }
    app = init_app(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def test_user(app):
    with app.app_context():
        auth_key = 'TOKEN-1'
        user1 = User(name='user1', auth_key=auth_key)
        db.session.add(user1)
        db.session.commit()
        
        yield user1

        db.session.delete(user1)


@pytest.fixture(scope="session")
def test_user_token(test_user):
    return ApiKey.makeApiKey(test_user.id, 'TOKEN-1')
