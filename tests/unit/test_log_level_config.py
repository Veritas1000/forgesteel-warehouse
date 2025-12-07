
import logging
import os
from unittest import mock

import pytest

from forgesteel_warehouse import init_app

@pytest.fixture(scope='function')
def mock_log_level_env(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            'LOG_LEVEL': 'DEBUG',
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield

def test_log_level_defaults_to_error():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'LOG_LEVEL': '',
    }
    app = init_app(test_config)

    logger = logging.getLogger('forgesteel_warehouse')

    assert logger.level == logging.ERROR

def test_log_level_can_be_set_from_env(mock_log_level_env):
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    }
    app = init_app(test_config)
    
    logger = logging.getLogger('forgesteel_warehouse')

    assert logger.level == logging.DEBUG

def test_log_level_can_be_set_from_config():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'LOG_LEVEL': 'INFO',
    }
    app = init_app(test_config)

    logger = logging.getLogger('forgesteel_warehouse')

    assert logger.level == logging.INFO

def test_log_level_config_overrides_env(mock_log_level_env):
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'LOG_LEVEL': 'INFO',
    }
    app = init_app(test_config)

    logger = logging.getLogger('forgesteel_warehouse')

    assert logger.level == logging.INFO
