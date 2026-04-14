from Ward_DND_AI.gui.universe.timeline.controller_timeline import TimelineController
from Ward_DND_AI.gui.universe.timeline.view_timeline import TimelineView


def test_timeline_controller_init(qapp, config, storage, ai):
    """TimelineController should instantiate without errors."""
    view = TimelineView(None, config)
    ctrl = TimelineController(view, ai, storage, config)
    assert ctrl is not None
