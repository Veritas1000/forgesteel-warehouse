import re
import tempfile

import requests
from testcontainers.generic import ServerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

## Tests the 'upgrade path' from the latest public image to the current state
def test_app_upgrade_path(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        public_container = ServerContainer(port=5000, image='veritas1000/forgesteel-warehouse:latest')
        public_container.with_volume_mapping(temp_directory, "/data", "rw")
        public_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        api_token = None
        test_data = [ { 'foo': 'bar' } ]
        with public_container:
            ## get auth token
            log = public_container.get_stdout()
            token = re.search(r"^\$1\$[0-9a-f]+$", log, re.MULTILINE)
            if token is not None:
                api_token = token.group(0)
            
            assert api_token is not None
            
            ## Connect
            url = public_container._create_connection_url()
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
        latest_container.with_volume_mapping(temp_directory, "/data", "rw")
        latest_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        with latest_container:
            ## Connect
            url = latest_container._create_connection_url()
            connect_headers = {'Authorization': f"Bearer {api_token}"}
            cr = requests.get(f"{url}/connect", headers=connect_headers)
            access_token = cr.json()['access_token']
            
            assert cr.status_code == 200
            assert access_token is not None

            ## Verify previous data
            get_req = requests.get(f"{url}/data/forgesteel-heroes", headers=headers)

            assert get_req.status_code == 200
            assert get_req.json()['data'] == test_data
