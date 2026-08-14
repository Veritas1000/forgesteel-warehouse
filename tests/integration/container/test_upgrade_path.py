import tempfile

import requests
from testcontainers.core.wait_strategies import HttpWaitStrategy
from testcontainers.generic import ServerContainer

from tests.integration.utils import get_api_token, get_csrf_access_token_from_response


## Tests the 'upgrade path' from the latest public image to the current state
def test_app_upgrade_path_latest(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        public_container = ServerContainer(port=5000, image='docker.io/veritas1000/forgesteel-warehouse:latest')
        public_container.with_env('COOKIE_SECURE', 'False')
        public_container.with_volume_mapping(temp_directory, "/data", "rw")
        public_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        ## Make sure we pull the latest image
        public_container._docker.client.images.pull('veritas1000/forgesteel-warehouse', tag='latest')

        api_token = None
        test_data = [
            {"id": "abcd123", "foo": "bar"},
            {"id": "12345-qwerty", "name": "FooBar"},
        ]
        with (public_container, requests.Session() as session):
            ## get auth token
            api_token = get_api_token(public_container)
            assert api_token is not None

            ## Connect
            url = public_container._create_connection_url()
            connect_headers = {'Authorization': f"Bearer {api_token}"}
            cr = session.post(f"{url}/connect", headers=connect_headers)
            csrf_token = get_csrf_access_token_from_response(cr)
            headers = {'X-CSRF-TOKEN': csrf_token} if csrf_token is not None else None

            ## Add some data
            add_req = session.put(f"{url}/data/forgesteel-heroes", json=test_data, headers=headers)
            assert add_req.status_code == 204

            ## Confirm via GET
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)
            assert get_req.status_code == 200
            assert get_req.json()['data'] == test_data

        latest_container = ServerContainer(port=5000, image=app_image)
        latest_container.with_env('COOKIE_SECURE', 'False')
        latest_container.with_volume_mapping(temp_directory, "/data", "rw")
        latest_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        with (latest_container, requests.Session() as session):
            ## Connect
            url = latest_container._create_connection_url()
            connect_headers = {'Authorization': f"Bearer {api_token}"}
            cr = session.post(f"{url}/connect", headers=connect_headers)
            csrf_token = get_csrf_access_token_from_response(cr)
            headers = {'X-CSRF-TOKEN': csrf_token} if csrf_token is not None else None

            ## Verify previous data
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()['data'] == test_data


## Tests the 'upgrade path' for 1.7 (splitting the heroes and homebrew tables)
def test_app_upgrade_path_1_7(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        public_container = ServerContainer(
            port=5000, image="docker.io/veritas1000/forgesteel-warehouse:1.6.2"
        )
        public_container.with_env("COOKIE_SECURE", "False")
        public_container.with_volume_mapping(temp_directory, "/data", "rw")
        public_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        api_token = None
        test_heroes_data = [
            {"id": "abcd123", "foo": "bar"},
            {"id": "12345-qwerty", "name": "FooBar"},
        ]
        test_homebrew_data = [
            {"id": "brew-234", "foo": "sdlfi"},
            {"id": "brew-w098u", "name": "zldjxshfoi"},
        ]
        with public_container, requests.Session() as session:
            ## get auth token
            api_token = get_api_token(public_container)
            assert api_token is not None

            ## Connect
            url = public_container._create_connection_url()
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
                f"{url}/data/forgesteel-homebrew-settings", json=test_homebrew_data, headers=headers
            )
            assert add_req.status_code == 204

            ## Confirm via GET
            get_req = session.get(f"{url}/data/forgesteel-homebrew-settings", headers=headers)
            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_homebrew_data

        latest_container = ServerContainer(port=5000, image=app_image)
        latest_container.with_env("COOKIE_SECURE", "False")
        latest_container.with_volume_mapping(temp_directory, "/data", "rw")
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
            get_req = session.get(f"{url}/data/forgesteel-homebrew-settings", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_homebrew_data

            get_req = session.get(
                f"{url}/data/forgesteel-homebrew-settings/brew-w098u", headers=headers
            )

            assert get_req.status_code == 200
            assert get_req.json()["data"]["name"] == "zldjxshfoi"


def test_app_upgrade_path_1_4(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        public_container = ServerContainer(
            port=5000, image="docker.io/veritas1000/forgesteel-warehouse:1.4.1"
        )
        public_container.with_env("JWT_COOKIE_SECURE", "False")
        public_container.with_volume_mapping(temp_directory, "/data", "rw")
        public_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        ## Make sure we pull the latest image
        public_container._docker.client.images.pull(
            "veritas1000/forgesteel-warehouse", tag="latest"
        )

        api_token = None
        test_data = [
            {"id": "abcd123", "foo": "bar"},
            {"id": "12345-qwerty", "name": "FooBar"},
        ]
        with public_container, requests.Session() as session:
            ## get auth token
            api_token = get_api_token(public_container)
            assert api_token is not None

            ## Connect
            url = public_container._create_connection_url()
            connect_headers = {"Authorization": f"Bearer {api_token}"}
            cr = session.post(f"{url}/connect", headers=connect_headers)
            csrf_token = get_csrf_access_token_from_response(cr)
            headers = {"X-CSRF-TOKEN": csrf_token} if csrf_token is not None else None

            ## Add some data
            add_req = session.put(
                f"{url}/data/forgesteel-heroes", json=test_data, headers=headers
            )
            assert add_req.status_code == 204

            ## Confirm via GET
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)
            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_data

        latest_container = ServerContainer(port=5000, image=app_image)
        latest_container.with_env("COOKIE_SECURE", "False")
        latest_container.with_volume_mapping(temp_directory, "/data", "rw")
        latest_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        with latest_container, requests.Session() as session:
            ## Connect
            url = latest_container._create_connection_url()
            connect_headers = {"Authorization": f"Bearer {api_token}"}
            cr = session.post(f"{url}/connect", headers=connect_headers)
            csrf_token = get_csrf_access_token_from_response(cr)
            headers = {"X-CSRF-TOKEN": csrf_token} if csrf_token is not None else None

            ## Verify previous data
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()["data"] == test_data


def test_app_upgrade_path_pre_1_0(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        early_container = ServerContainer(port=5000, image='veritas1000/forgesteel-warehouse:0.1.6')
        early_container.with_volume_mapping(temp_directory, "/data", "rw")
        early_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        api_token = None
        test_data = [
            {"id": "abcd123", "foo": "bar"},
            {"id": "12345-qwerty", "name": "FooBar"},
        ]
        with (early_container):
            ## get auth token
            api_token = get_api_token(early_container)

            assert api_token is not None

            ## Connect
            url = early_container._create_connection_url()
            connect_headers = {'Authorization': f"Bearer {api_token}"}
            cr = requests.get(f"{url}/connect", headers=connect_headers)
            access_token = cr.json()['access_token']
            assert cr.status_code == 200
            assert access_token is not None

            ## Add some data
            headers = {'Authorization': f"Bearer {access_token}"}
            add_req = requests.put(f"{url}/data/forgesteel-heroes", json=test_data, headers=headers)

            assert add_req.status_code == 204
            ## Confirm via GET
            get_req = requests.get(f"{url}/data/forgesteel-heroes", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()['data'] == test_data

        latest_container = ServerContainer(port=5000, image=app_image)
        latest_container.with_env('COOKIE_SECURE', 'False')
        latest_container.with_volume_mapping(temp_directory, "/data", "rw")
        latest_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        with (latest_container, requests.Session() as session):
            ## Connect
            url = latest_container._create_connection_url()
            connect_headers = {'Authorization': f"Bearer {api_token}"}
            cr = session.post(f"{url}/connect", headers=connect_headers)
            csrf_token = get_csrf_access_token_from_response(cr)
            headers = {'X-CSRF-TOKEN': csrf_token} if csrf_token is not None else None

            ## Verify previous data
            get_req = session.get(f"{url}/data/forgesteel-heroes", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()['data'] == test_data
