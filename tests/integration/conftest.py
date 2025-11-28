import tempfile
import pytest
import re

from testcontainers.generic import ServerContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.wait_strategies import HttpWaitStrategy, LogMessageWaitStrategy

@pytest.fixture(scope='session')
def app_image():
    with DockerImage(path='.', dockerfile_path='Containerfile', tag='testing/fs-warehouse:latest', clean_up=True) as image:
        yield image

@pytest.fixture(scope='session')
def app_container(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        app_container = ServerContainer(port=5000, image=app_image)
        app_container.with_volume_mapping(temp_directory, "/data", "rw")
        app_container.waiting_for(HttpWaitStrategy(5000, "/healthz"))

        with app_container:
            yield app_container

@pytest.fixture(scope='session', autouse=True)
def api_token(app_container):
    stdout_bytes, stderr_bytes = app_container.get_logs()
    log = stdout_bytes.decode() if stdout_bytes else ""
    token = re.search(r"^\$1\$[0-9a-f]+$", log, re.MULTILINE)

    return token.group(0) if token is not None else None