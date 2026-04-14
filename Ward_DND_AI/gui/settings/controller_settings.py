from Ward_DND_AI.gui.settings.app.controller_app import AppSettingsController
from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes


class SettingsController:
    def __init__(self, view, config, ai_engine=None, storage_backend=None):
        self.view = view
        self.config = config
        self.ai_engine = ai_engine
        self.storage_backend = storage_backend

        # Initialize subcontrollers with their views and shared resources
        from Ward_DND_AI.gui.settings.ai.controller_ai import AIController
        from Ward_DND_AI.gui.settings.campaign.controller_campaign_settings import (
            CampaignSettingsController,
        )
        from Ward_DND_AI.gui.settings.help.controller_help import HelpController

        self.controllers = {}

        self.controllers["ai"] = AIController(self.view.ai_view, self.config, self.ai_engine, self.storage_backend)
        self.controllers["campaign"] = CampaignSettingsController(
            self.view.campaign_view, self.config, self.ai_engine, self.storage_backend
        )
        self.controllers["help"] = HelpController(
            self.view.help_view, self.config, self.ai_engine, self.storage_backend
        )
        self.controllers["app"] = AppSettingsController(
            self.view.app_settings_view,
            self.config,
            None,  # pass QApplication.instance() if you need the app
        )

        # Setup stacked widget and button group for switching tabs
        self.view.stacked_widget.addWidget(self.view.ai_view)
        self.view.stacked_widget.addWidget(self.view.campaign_view)
        self.view.stacked_widget.addWidget(self.view.help_view)
        self.view.stacked_widget.insertWidget(0, self.view.app_settings_view)  # Or correct index for your layout

        # Connect tab buttons
        self.view.btn_ai.clicked.connect(catch_and_report_crashes(lambda checked=False: self.switch_tab("ai")))
        self.view.btn_campaign.clicked.connect(
            catch_and_report_crashes(lambda checked=False: self.switch_tab("campaign"))
        )
        self.view.btn_help.clicked.connect(catch_and_report_crashes(lambda checked=False: self.switch_tab("help")))
        self.view.btn_app.clicked.connect(catch_and_report_crashes(lambda checked=False: self.switch_tab("app")))

        # Start with AI tab selected
        self.switch_tab("ai")
        self._update_button_states("ai")

        # Setup config change handling if config supports signals or callbacks (optional)
        # Example:
        # self.config.config_changed.connect(self.on_config_changed)

    def switch_tab(self, tab_name):
        if tab_name == "ai":
            self.view.stacked_widget.setCurrentWidget(self.view.ai_view)
            self._update_button_states("ai")
        elif tab_name == "campaign":
            self.view.stacked_widget.setCurrentWidget(self.view.campaign_view)
            self._update_button_states("campaign")
        elif tab_name == "help":
            self.view.stacked_widget.setCurrentWidget(self.view.help_view)
            self._update_button_states("help")
        elif tab_name == "app":
            self.view.stacked_widget.setCurrentWidget(self.view.app_settings_view)
            self._update_button_states("app")

    @catch_and_report_crashes
    def _update_button_states(self, active_tab):
        self.view.btn_ai.setEnabled(active_tab != "ai")
        self.view.btn_campaign.setEnabled(active_tab != "campaign")
        self.view.btn_help.setEnabled(active_tab != "help")
        self.view.btn_app.setEnabled(active_tab != "app")

    # Optional: method to handle config changes at runtime
    def on_config_changed(self, key, value):
        # Example: react to config changes if needed
        pass
