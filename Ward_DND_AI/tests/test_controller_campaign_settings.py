from Ward_DND_AI.gui.campaign_settings.controller_campaign_settings import (
    CampaignSettingsController,
)
from Ward_DND_AI.gui.campaign_settings.view_campaign_settings import (
    CampaignSettingsView,
)


def test_save_updates_config(tmp_path, tk_root):
    # create a fresh config
    from Ward_DND_AI.config.config import Config

    cfg = Config()
    cfg.VAULT_PATH = ""
    cfg.OPENAI_API_KEY = ""
    view = CampaignSettingsView(tk_root, cfg)
    ctrl = CampaignSettingsController(view, cfg)

    # enter new values
    view.vault_entry.delete(0, "end")
    view.vault_entry.insert(0, str(tmp_path / "vault"))
    view.api_entry.delete(0, "end")
    view.api_entry.insert(0, "sk-test")

    # call save
    ctrl.on_save()

    assert cfg.VAULT_PATH.endswith("vault")
    assert cfg.OPENAI_API_KEY == "sk-test"
