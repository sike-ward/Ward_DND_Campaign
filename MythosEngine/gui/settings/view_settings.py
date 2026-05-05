# MythosEngine/gui/settings/view_settings.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.settings.account.view_account import AccountSettingsView
from MythosEngine.gui.settings.ai.view_ai import AISettingsView
from MythosEngine.gui.settings.app.view_app import AppSettingsView
from MythosEngine.gui.settings.campaign.view_campaign import CampaignSettingsView
from MythosEngine.gui.settings.help.view_help import HelpView
from MythosEngine.gui.settings.users.view_users import UserManagementView

# Stacked widget indices — keep in sync with _build_sidebar
IDX_APP = 0
IDX_ACCOUNT = 1
IDX_AI = 2
IDX_CAMPAIGN = 3
IDX_HELP = 4
IDX_USERS = 5


class SettingsView(QWidget):
    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx = ctx
        self.config = ctx.config

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Inner sidebar (inside Settings panel) ────────────────────────
        self.sidebar = QFrame(self)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(210)

        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(12, 20, 12, 16)
        sb_layout.setSpacing(4)

        section_label = QLabel("SETTINGS")
        section_label.setObjectName("NavSectionLabel")
        sb_layout.addWidget(section_label)
        sb_layout.addSpacing(8)

        self._nav_btns: list[tuple[QPushButton, int]] = []

        def _nav(label: str, idx: int) -> QPushButton:
            btn = QPushButton(label)
            btn.setObjectName("NavBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda _=False, i=idx: self.switch_tab(i))
            sb_layout.addWidget(btn)
            self._nav_btns.append((btn, idx))
            return btn

        self.btn_app = _nav("⚙️   App Settings", IDX_APP)
        self.btn_account = _nav("🔒  My Account", IDX_ACCOUNT)
        self.btn_ai = _nav("✦   AI Settings", IDX_AI)
        self.btn_campaign = _nav("🗺️   Campaign", IDX_CAMPAIGN)
        self.btn_help = _nav("❓  Help & About", IDX_HELP)
        self.btn_users = _nav("👥  User Management", IDX_USERS)

        sb_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        # ── Stacked content area ─────────────────────────────────────────
        self.stacked_widget = QStackedWidget(self)

        # Order MUST match IDX_* constants above
        self.app_settings_view = AppSettingsView(self, self.config)
        self.account_view = AccountSettingsView(self)
        self.ai_view = AISettingsView(self, self.ctx)
        self.campaign_view = CampaignSettingsView(self, self.config)
        self.help_view = HelpView(self, self.config)
        self.users_view = UserManagementView(self)

        self.stacked_widget.addWidget(self.app_settings_view)  # 0
        self.stacked_widget.addWidget(self.account_view)  # 1
        self.stacked_widget.addWidget(self.ai_view)  # 2
        self.stacked_widget.addWidget(self.campaign_view)  # 3
        self.stacked_widget.addWidget(self.help_view)  # 4
        self.stacked_widget.addWidget(self.users_view)  # 5

        main_layout.addWidget(self.stacked_widget, 1)

        # Start on App Settings
        self.switch_tab(IDX_APP)

    # ── Navigation ────────────────────────────────────────────────────────

    def switch_tab(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        for btn, idx in self._nav_btns:
            active = idx == index
            btn.setProperty("active", "true" if active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
