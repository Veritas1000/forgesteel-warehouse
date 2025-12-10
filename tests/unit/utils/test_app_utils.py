
import json
import os
import tempfile
from unittest import mock

import pytest

from forgesteel_warehouse.utils.app_utils import create_or_load_config


@pytest.fixture()
def temp_config_dir():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory

@pytest.fixture()
def temp_config_file(temp_config_dir, monkeypatch: pytest.MonkeyPatch):
    configpath = os.path.join(temp_config_dir, 'config.json')
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            'FSW_CONFIG_PATH': configpath,
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)

        yield configpath

def test_bootstrap_creates_config_if_none(temp_config_file):
        assert not os.path.exists(temp_config_file)

        create_or_load_config()
        
        assert os.path.exists(temp_config_file)

def test_bootstrap_writes_secrets_if_none(temp_config_file):
        config = {
             'FOO': 'bar'
        }
        with open(temp_config_file, 'w') as configfile:
            json.dump(config, configfile)

        create_or_load_config()
        
        assert os.path.exists(temp_config_file)

        with open(temp_config_file, 'r') as configfile:
            newconfig = json.load(configfile)

            assert 'SECRET_KEY' in newconfig
            assert 'JWT_SECRET_KEY' in newconfig
            assert newconfig['FOO'] == 'bar'
