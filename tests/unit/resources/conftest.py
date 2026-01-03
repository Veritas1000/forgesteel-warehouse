from unittest.mock import Mock, patch
from flask_migrate import upgrade
import pytest

from forgesteel_warehouse import init_app, db
from forgesteel_warehouse.utils.patreon_api import PatreonApi

@pytest.fixture()
def patreon_api():
    with patch.object(PatreonApi, '__new__', return_value=Mock(spec=PatreonApi)) as mock:
        yield mock.return_value


@pytest.fixture()
def cookie_check_client():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_ACCESS_COOKIE_NAME': 'JWT_ACCESS_COOKIE',
        'JWT_REFRESH_COOKIE_NAME': 'JWT_REFRESH_COOKIE',
        'JWT_ACCESS_CSRF_COOKIE_NAME': 'JWT_ACCESS_CSRF_COOKIE'
    }
    app = init_app(test_config)
    
    with app.app_context():
        upgrade()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
