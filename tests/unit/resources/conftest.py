from typing import Any, Generator
from unittest.mock import Mock, patch
import pytest

from forgesteel_warehouse.utils.patreon_api import PatreonApi

@pytest.fixture()
def patreon_api():
    with patch.object(PatreonApi, '__new__', return_value=Mock(spec=PatreonApi)) as mock:
        yield mock.return_value