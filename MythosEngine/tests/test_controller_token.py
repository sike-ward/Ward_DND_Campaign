from MythosEngine.gui.token.controller_token import TokenController
from MythosEngine.gui.token.view_token import TokenView


def test_token_shows_usage(tk_root, config, storage):
    view = TokenView(tk_root, config)

    class DummyAI:
        session_tokens = 5

    _ = TokenController(view, DummyAI(), storage, config)
    assert "Sessions:" in view.usage_label.cget("text")
