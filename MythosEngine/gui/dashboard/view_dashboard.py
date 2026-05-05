# MythosEngine/gui/dashboard/view_dashboard.py
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import (
    GlowButton,
    SectionHeader,
    ShadowCard,
    StatCard,
    Tok,
)


class DashboardView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 32)
        root.setSpacing(28)

        # ── Header ─────────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header = SectionHeader("Dashboard", "Welcome back — here's your campaign at a glance.")
        header_row.addWidget(header)
        header_row.addStretch()

        self.btn_refresh = GlowButton("↻  Refresh", "secondary")
        self.btn_refresh.setFixedWidth(120)
        header_row.addWidget(self.btn_refresh, alignment=Qt.AlignmentFlag.AlignBottom)

        root.addLayout(header_row)

        # ── Stat cards row ─────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)

        self.stat_notes = StatCard("📝", "Notes", "—", accent=QColor("#7C5CFC"))
        self.stat_folders = StatCard("📁", "Folders", "—", accent=QColor("#10B981"))
        self.stat_characters = StatCard("🧙", "Characters", "—", accent=QColor("#F59E0B"))
        self.stat_sessions = StatCard("🎲", "Sessions", "—", accent=QColor("#3B82F6"))

        for card in (self.stat_notes, self.stat_folders, self.stat_characters, self.stat_sessions):
            cards_row.addWidget(card)

        root.addLayout(cards_row)

        # ── Bottom row: Recent + Quick Actions ────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(24)

        # Recent notes — ShadowCard
        recent_card = ShadowCard(shadow_blur=18)
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(22, 20, 22, 18)
        recent_layout.setSpacing(12)

        recent_header = QLabel("Recent Notes")
        rh_font = QFont("Segoe UI", 11)
        rh_font.setWeight(QFont.Weight.DemiBold)
        recent_header.setFont(rh_font)
        recent_header.setStyleSheet(f"color: {Tok.TEXT.name()}; background: transparent;")
        recent_layout.addWidget(recent_header)

        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("QListWidget { background: transparent; border: none; padding: 0; }")
        self.recent_list.setMaximumHeight(240)
        recent_layout.addWidget(self.recent_list)

        bottom_row.addWidget(recent_card, 3)

        # Quick actions panel — ShadowCard
        actions_card = ShadowCard(shadow_blur=18)
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(22, 20, 22, 18)
        actions_layout.setSpacing(12)

        actions_header = QLabel("Quick Actions")
        actions_header.setFont(rh_font)
        actions_header.setStyleSheet(f"color: {Tok.TEXT.name()}; background: transparent;")
        actions_layout.addWidget(actions_header)

        self.btn_new_note = GlowButton("✏️   New Note", "primary")
        self.btn_browse = GlowButton("📖   Browse Vault", "secondary")
        self.btn_ask_ai = GlowButton("✦   Ask AI", "success")

        for btn in (self.btn_new_note, self.btn_browse, self.btn_ask_ai):
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setMinimumHeight(42)
            actions_layout.addWidget(btn)

        actions_layout.addStretch()
        bottom_row.addWidget(actions_card, 2)

        root.addLayout(bottom_row)

        # ── Status ─────────────────────────────────────────────────────────
        self.status_label = QLabel("")
        self.status_label.setProperty("role", "muted")
        root.addWidget(self.status_label)

        root.addStretch()

    # ── Public API (controller uses these) ─────────────────────────────────

    def set_stat(self, card, value: str):
        """Backward-compatible stat updater. Works with StatCard and old QFrame."""
        if isinstance(card, StatCard):
            card.set_value(value)
        elif hasattr(card, "_value_label"):
            card._value_label.setText(value)
