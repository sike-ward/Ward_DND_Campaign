import pytest

from MythosEngine.gui.campaign_settings.controller_campaign_settings import (
    CampaignSettingsController,
)
from MythosEngine.gui.campaign_settings.view_campaign_settings import (
    CampaignSettingsView,
)
from MythosEngine.gui.help.controller_help import HelpController
from MythosEngine.gui.help.view_help import HelpView
from MythosEngine.gui.random_generator.controller_random_generator import (
    RandomGeneratorController,
)
from MythosEngine.gui.random_generator.view_random_generator import RandomGeneratorView
from MythosEngine.gui.summarize.controller_summarize import SummarizeController
from MythosEngine.gui.summarize.view_summarize import SummarizeView
from MythosEngine.gui.timeline.controller_timeline import TimelineController
from MythosEngine.gui.timeline.view_timeline import TimelineView
from MythosEngine.gui.token.controller_token import TokenController
from MythosEngine.gui.token.view_token import TokenView

CASES = [
    (SummarizeView, SummarizeController, "on_summarize", []),
    (RandomGeneratorView, RandomGeneratorController, "on_generate", []),
    (TimelineView, TimelineController, "add_event", []),
    (CampaignSettingsView, CampaignSettingsController, "on_save", []),
    (HelpView, HelpController, "_populate", []),
    (TokenView, TokenController, "update_usage", []),
]


@pytest.mark.parametrize("View,Ctrl,method,args", CASES)
def test_controller_methods_dont_crash(tk_root, config, storage, ai, View, Ctrl, method, args):
    view = View(tk_root, config)
    try:
        ctrl = Ctrl(view, ai(), storage, config)
    except TypeError:
        # some controllers only take (view, config)
        ctrl = Ctrl(view, config)
    getattr(ctrl, method)(*args)
