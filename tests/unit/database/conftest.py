import flask_migrate
import pytest

from forgesteel_warehouse import init_app


@pytest.fixture()
def alembic_config():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    }
    app = init_app(test_config)

    with app.app_context():
        migrate = flask_migrate.Migrate(directory="migrations")
        cfg = migrate.get_config()
        yield cfg
