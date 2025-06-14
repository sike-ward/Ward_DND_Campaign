from Ward_DND_AI.gui.help.controller_help import HelpController
from Ward_DND_AI.gui.help.view_help import HelpView


def test_help_populates_text(tk_root, config):
    view = HelpView(tk_root, config)
    _ = HelpController(view, config)
    content = view.box.get("1.0", "end")
    assert "Welcome to the Obsidian Lore Assistant" in content
