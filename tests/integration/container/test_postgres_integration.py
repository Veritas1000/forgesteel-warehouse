import requests
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import HttpWaitStrategy
from testcontainers.generic import ServerContainer

from tests.integration.utils import (
    get_api_token,
    get_csrf_access_token_from_response,
    get_csrf_headers,
)


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
        app_container.with_env('COOKIE_SECURE', 'False')
        app_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        test_data = [ { 'foo': 'bar' } ]
        with app_container:
            headers = get_csrf_headers(app_container, session)
            url = app_container._create_connection_url()

            ## Add some data
            add_req = session.put(f"{url}/data/forgesteel-hidden-setting-ids", json=test_data, headers=headers)
            
            assert add_req.status_code == 204

            ## Confirm via GET
            get_req = session.get(f"{url}/data/forgesteel-hidden-setting-ids", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()['data'] == test_data

def test_postgres_upgrade_1_7(app_image):
    with (
        Network() as network,
        PostgresContainer('postgres:18', username='test_user', password='Password!', dbname='test_db')
        .with_name('db')
        .with_network(network) as postgres,
        requests.Session() as session
    ):
        db_url = 'postgresql://test_user:Password!@db/test_db'

        before_container = ServerContainer(
            port=5000, image="docker.io/veritas1000/forgesteel-warehouse:1.6.2"
        )
        before_container.with_network(network)
        before_container.with_env('DATABASE_URI', db_url)
        before_container.with_env('COOKIE_SECURE', 'False')
        before_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        api_token = None
        test_heroes_data = [
            {"id": "abcd123", "foo": "bar"},
            {"id": "12345-qwerty", "name": "FooBar"},
        ]
        test_homebrew_data = [
            {"id": "brew-234", "foo": "sdlfi"},
            {"id": "brew-w098u", "name": "zldjxshfoi"},
        ]

        with before_container, requests.Session() as session:
            ## get auth token
            api_token = get_api_token(before_container)
            assert api_token is not None

            ## Connect
            url = before_container._create_connection_url()
            connect_headers = {"Authorization": f"Bearer {api_token}"}
            cr = session.post(f"{url}/connect", headers=connect_headers)
            csrf_token = get_csrf_access_token_from_response(cr)
            headers = {"X-CSRF-TOKEN": csrf_token} if csrf_token is not None else None

            ## Heroes
            ## Add some data
            add_req = session.put(
                f"{url}/data/forgesteel-heroes", json=test_heroes_data, headers=headers
            )
            assert add_req.status_code == 204

            ## Confirm via GET
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)
            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_heroes_data

            ## Homebrew
            ## Add some data
            add_req = session.put(
                f"{url}/data/forgesteel-homebrew-settings",
                json=test_homebrew_data,
                headers=headers,
            )
            assert add_req.status_code == 204

            ## Confirm via GET
            get_req = session.get(
                f"{url}/data/forgesteel-homebrew-settings", headers=headers
            )
            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_homebrew_data

        latest_container = ServerContainer(port=5000, image=app_image)
        latest_container.with_env("COOKIE_SECURE", "False")
        latest_container.with_network(network)
        latest_container.with_env('DATABASE_URI', db_url)
        latest_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        with latest_container, requests.Session() as session:
            ## Connect
            url = latest_container._create_connection_url()
            connect_headers = {"Authorization": f"Bearer {api_token}"}
            cr = session.post(f"{url}/connect", headers=connect_headers)
            csrf_token = get_csrf_access_token_from_response(cr)
            headers = {"X-CSRF-TOKEN": csrf_token} if csrf_token is not None else None

            ## Verify previous data
            ## Heroes
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_heroes_data

            get_req = session.get(f"{url}/data/forgesteel-heroes/abcd123", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()["data"]["foo"] == "bar"

            ## Homebrew
            get_req = session.get(
                f"{url}/data/forgesteel-homebrew-settings", headers=headers
            )

            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_homebrew_data

            get_req = session.get(
                f"{url}/data/forgesteel-homebrew-settings/brew-w098u", headers=headers
            )

            assert get_req.status_code == 200
            assert get_req.json()["data"]["name"] == "zldjxshfoi"
