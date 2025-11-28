import re
import tempfile

from testcontainers.core.wait_strategies import HttpWaitStrategy
from testcontainers.core.container import DockerContainer

def test_bootstrap_first_run(app_image):
    container = DockerContainer(str(app_image), ports=[5000], _wait_strategy=HttpWaitStrategy(5000, "/healthz"))
    with container:
        stdout_bytes, stderr_bytes = container.get_logs()
        log = stdout_bytes.decode() if stdout_bytes else ""

        assert re.search(r"^USER CREATED$", log, re.MULTILINE), "'USER CREATED' not found in logs"
        assert re.search(r"Here is your API KEY", log, re.MULTILINE), "api key instructions not found in logs"
        assert re.search(r"^\$1\$[0-9a-f]+$", log, re.MULTILINE), "api key not found in logs"

def test_bootstrap_multiple_runs(app_image):
    with tempfile.TemporaryDirectory() as temp_directory:
        container = DockerContainer(str(app_image), ports=[5000], _wait_strategy=HttpWaitStrategy(5000, "/healthz"))
        container.with_volume_mapping(temp_directory, "/data", "rw")
        with container:
            stdout_bytes, stderr_bytes = container.get_logs()
            log = stdout_bytes.decode() if stdout_bytes else ""

            assert re.search(r"^USER CREATED$", log, re.MULTILINE), "'USER CREATED' not found in logs on first run"
        
        container2 = DockerContainer(str(app_image), ports=[5000], _wait_strategy=HttpWaitStrategy(5000, "/healthz"))
        container2.with_volume_mapping(temp_directory, "/data", "rw")

        with container2:
            stdout_bytes, stderr_bytes = container2.get_logs()
            log = stdout_bytes.decode() if stdout_bytes else ""

            assert 'USER CREATED' not in log
