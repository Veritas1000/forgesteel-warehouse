import logging
import tempfile
import pytest
import re

import requests
from testcontainers.generic import ServerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.wait_strategies import HttpWaitStrategy

from tests.integration.utils import get_csrf_access_token_from_response

log = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def app_image():
    with DockerImage(path='.', dockerfile_path='Containerfile', tag='testing/fs-warehouse:latest', clean_up=True) as image:
        yield image

@pytest.fixture(scope='session')
def app_container(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        app_container = ServerContainer(port=5000, image=app_image)
        app_container.with_env('JWT_COOKIE_SECURE', 'False')
        app_container.with_env('LOG_LEVEL', 'DEBUG')
        app_container.with_volume_mapping(temp_directory, "/data", "rw")
        app_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        with app_container:
            yield app_container

@pytest.fixture(scope='session')
def api_token(app_container):
    container_log = app_container.get_stdout()
    log.debug(container_log)
    token = re.search(r"^\$1\$[0-9a-f]+$", container_log, re.MULTILINE)

    return token.group(0) if token is not None else None

@pytest.fixture(scope="session")
def container_url(app_container):
    return app_container._create_connection_url()

@pytest.fixture(scope="session")
def requests_session():
    with requests.Session() as session:
        yield session

@pytest.fixture(scope="session")
def csrf_headers(container_url, api_token, requests_session):
    connect_headers = {'Authorization': f"Bearer {api_token}"}
    cr = requests_session.post(f"{container_url}/connect", headers=connect_headers)

    if not cr.ok:
        log.debug(cr.request.headers)
        log.debug(cr.headers)
        log.debug(cr.cookies.get_dict())
        log.debug(cr.content)

    token = get_csrf_access_token_from_response(cr)
    assert cr.status_code == 200
    assert token is not None

    headers = {'X-CSRF-TOKEN': token}
    return headers

@pytest.fixture(scope="session")
def auth_headers(container_url, api_token):
    connect_headers = {'Authorization': f"Bearer {api_token}"}
    cr = requests.post(f"{container_url}/connect", headers=connect_headers)

    if not cr.ok:
        log.debug(cr.request.headers)
        log.debug(cr.headers)
        log.debug(cr.cookies.get_dict())
        log.debug(cr.content)

    access_token = cr.json()['access_token']
    assert cr.status_code == 200
    assert access_token is not None

    headers = {'Authorization': f"Bearer {access_token}"}
    return headers

@pytest.fixture(params=['csrf_headers', 'auth_headers'], scope="session")
def user_headers(request):
    return request.getfixturevalue(request.param)

@pytest.fixture(autouse=True)
def capture_logs(caplog):
    caplog.set_level(logging.DEBUG)
