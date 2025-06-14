# tests/test_smoke.py
from Ward_DND_AI.gui.gui import LoreMainApp


def test_app_instantiates():
    app = LoreMainApp()
    assert app is not None
