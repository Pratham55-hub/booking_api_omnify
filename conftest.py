# ==============================================================================
#  FILE: conftest.py
#  DESCRIPTION: Shared fixtures for pytest.
# ==============================================================================
import pytest
from app import create_app

@pytest.fixture(scope='module')
def app():
    """
    Create and configure a new app instance for each test module.
    The 'module' scope means this fixture will be set up once per test file.
    """
    app = create_app('config.TestingConfig')
    yield app
