# conftest.py
import os
import sys

# Ensure project root is on sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root not in sys.path:
    sys.path.insert(0, root)

import tkinter as tk

import pytest

from Ward_DND_AI.ai.ai_engine import LoreAI
from Ward_DND_AI.config.config import Config
from Ward_DND_AI.storage.old_storage import ObsidianStorage


@pytest.fixture(scope="session")
def config(tmp_path_factory):
    # Create a session-scoped temporary vault directory
    vault = tmp_path_factory.mktemp("vault")
    cfg = Config()
    cfg.VAULT_PATH = str(vault)
    return cfg


@pytest.fixture(scope="session")
def storage(config):
    return ObsidianStorage(config.VAULT_PATH)


@pytest.fixture(scope="session")
def ai():
    # Return the AI class; instantiation is done in tests
    return LoreAI


@pytest.fixture(scope="function")
def tk_root(monkeypatch):
    # Stub simpledialog.askstring to prevent blocking
    import tkinter.simpledialog as sd

    monkeypatch.setattr(sd, "askstring", lambda *args, **kwargs: None)

    # Stub messagebox to prevent popups during tests
    import tkinter.messagebox as mb

    monkeypatch.setattr(mb, "showinfo", lambda *args, **kwargs: None)
    monkeypatch.setattr(mb, "showerror", lambda *args, **kwargs: None)

    # Create and withdraw the root window so it doesn't display
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()
