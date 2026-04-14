# conftest.py
import os
import sys

# Ensure project root is on sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root not in sys.path:
    sys.path.insert(0, root)

import pytest

from Ward_DND_AI.config.config import Config
from Ward_DND_AI.storage.storage_router import get_storage_backend


@pytest.fixture(scope="session")
def config(tmp_path_factory):
    vault = tmp_path_factory.mktemp("vault")
    cfg = Config()
    cfg._data["VAULT_PATH"] = str(vault)
    cfg._data["VAULT_TYPE"] = "hybrid"
    cfg._data["OPENAI_API_KEY"] = "test-key"
    return cfg


@pytest.fixture(scope="session")
def storage(config):
    return get_storage_backend(config)


@pytest.fixture(scope="session")
def ai():
    """Return None as a placeholder AI engine for controller tests that don't call AI."""
    return None


@pytest.fixture
def qapp():
    """Provide a QApplication instance for GUI tests."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    yield app
