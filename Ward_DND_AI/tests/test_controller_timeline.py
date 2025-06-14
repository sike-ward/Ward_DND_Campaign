import tkinter.simpledialog as sd

from Ward_DND_AI.gui.timeline.controller_timeline import TimelineController
from Ward_DND_AI.gui.timeline.view_timeline import TimelineView


def test_add_event(monkeypatch, tk_root, config, storage, ai):
    view = TimelineView(tk_root, config)
    ctrl = TimelineController(view, ai(), storage, config)
    # simulate dialog returning "Event1"
    monkeypatch.setattr(sd, "askstring", lambda *a, **k: "Event1")
    ctrl.add_event()
    assert view.event_list.get(0) == "Event1"
