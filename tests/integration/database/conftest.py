import flask_migrate
import pytest
from testcontainers.core.network import Network
from testcontainers.postgres import PostgresContainer

from forgesteel_warehouse import init_app


@pytest.fixture()
def alembic_pg_config():
    with (
        Network() as network,
        PostgresContainer('postgres:18', username='test_user', password='Password!', dbname='test_db')
        .with_name('db')
        .with_network(network) as postgres
    ):
        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": postgres.get_connection_url(),
        }
        app = init_app(test_config)

        with app.app_context():
            migrate = flask_migrate.Migrate(directory="migrations")
            cfg = migrate.get_config()
            yield cfg
