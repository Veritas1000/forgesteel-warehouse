import requests

from testcontainers.postgres import PostgresContainer
from testcontainers.generic import ServerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import HttpWaitStrategy

from tests.integration.utils import get_csrf_headers

def test_postgres_connection(app_image):
    with (
        Network() as network,
        PostgresContainer('postgres:18', username='test_user', password='Password!', dbname='test_db')
        .with_name('db')
        .with_network(network) as postgres,
        requests.Session() as session
    ):
        db_url = 'postgresql://test_user:Password!@db/test_db'

        app_container = ServerContainer(port=5000, image=app_image)
        app_container.with_network(network)
        app_container.with_env('DATABASE_URI', db_url)
        app_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        test_data = [ { 'foo': 'bar' } ]
        with app_container:
            headers = get_csrf_headers(app_container, session)
            url = app_container._create_connection_url()

            ## Add some data
            add_req = session.put(f"{url}/data/forgesteel-heroes", json=test_data, headers=headers)
            
            assert add_req.status_code == 204

            ## Confirm via GET
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()['data'] == test_data
