from Ward_DND_AI.gui.summarize.controller_summarize import SummarizeController
from Ward_DND_AI.gui.summarize.view_summarize import SummarizeView


class DummyAI:
    def summarize(self, text):
        return text.upper()


def test_summarize_empty_shows_prompt(tk_root, config, storage):
    view = SummarizeView(tk_root, config)
    ctrl = SummarizeController(view, DummyAI(), storage, config)
    view.input_text.delete("1.0", "end")
    ctrl.on_summarize()
    assert view.output_text.get("1.0", "end").strip() == "[No input provided]"


def test_summarize_nonempty_transforms(tk_root, config, storage):
    view = SummarizeView(tk_root, config)
    ctrl = SummarizeController(view, DummyAI(), storage, config)
    view.input_text.insert("1.0", "hello")
    ctrl.on_summarize()
    assert view.output_text.get("1.0", "end").strip() == "HELLO"
