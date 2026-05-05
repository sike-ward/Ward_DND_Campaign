# MythosEngine/gui/settings/controller_settings.py
from MythosEngine.gui.settings.app.controller_app import AppSettingsController
from MythosEngine.gui.settings.view_settings import IDX_ACCOUNT, IDX_AI, IDX_APP, IDX_CAMPAIGN, IDX_HELP, IDX_USERS


class SettingsController:
    def __init__(self, view, ctx):
        self.view = view
        self.ctx = ctx
        self.config = ctx.config
        self.ai_engine = ctx.ai
        self.storage_backend = ctx.storage

        # ── Subcontrollers ────────────────────────────────────────────────
        from MythosEngine.gui.settings.account.controller_account import AccountSettingsController
        from MythosEngine.gui.settings.ai.controller_ai import AIController
        from MythosEngine.gui.settings.campaign.controller_campaign_settings import (
            CampaignSettingsController,
        )
        from MythosEngine.gui.settings.help.controller_help import HelpController
        from MythosEngine.gui.settings.users.controller_users import UserManagementController

        self.controllers: dict = {}
        self.controllers["app"] = AppSettingsController(self.view.app_settings_view, self.ctx, None)
        self.controllers["account"] = AccountSettingsController(self.view.account_view, self.ctx)
        self.controllers["ai"] = AIController(self.view.ai_view, self.ctx)
        self.controllers["campaign"] = CampaignSettingsController(self.view.campaign_view, self.ctx)
        self.controllers["help"] = HelpController(self.view.help_view, self.ctx)
        self.controllers["users"] = UserManagementController(self.view.users_view, self.ctx)

        # The view's __init__ already:
        #   - adds all 5 sub-views to stacked_widget (in IDX order)
        #   - connects nav buttons via _nav() → view.switch_tab(idx)
        #   - highlights App Settings as the default active tab
        # Nothing to duplicate here.

    # ── Public API ────────────────────────────────────────────────────────

    def switch_tab(self, tab_name: str) -> None:
        """Programmatic tab switch by name (e.g. from menu actions)."""
        mapping = {
            "app": IDX_APP,
            "account": IDX_ACCOUNT,
            "ai": IDX_AI,
            "campaign": IDX_CAMPAIGN,
            "help": IDX_HELP,
            "users": IDX_USERS,
        }
        idx = mapping.get(tab_name)
        if idx is not None:
            self.view.switch_tab(idx)

    def on_config_changed(self, key, value):
        pass
