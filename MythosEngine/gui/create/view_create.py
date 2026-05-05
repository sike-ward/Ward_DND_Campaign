# MythosEngine/gui/create/view_create.py
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.create.random_generator.view_random_generator import RandomGeneratorView
from MythosEngine.gui.widgets import SectionHeader, Tok


def _make_placeholder(icon: str, title: str, desc: str) -> QWidget:
    """Centered 'Coming Soon' placeholder for stub tabs."""
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(14)

    icon_lbl = QLabel(icon)
    icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_lbl.setStyleSheet("font-size: 40pt; background: transparent;")

    title_lbl = QLabel(title)
    title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_font = QFont("Segoe UI", 16)
    title_font.setWeight(QFont.Weight.Bold)
    title_lbl.setFont(title_font)
    title_lbl.setStyleSheet(f"color: {Tok.TEXT.name()}; background: transparent;")

    desc_lbl = QLabel(desc)
    desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    desc_lbl.setWordWrap(True)
    desc_lbl.setMaximumWidth(420)
    desc_lbl.setStyleSheet(f"color: {Tok.TEXT_SEC.name()}; font-size: 10pt; background: transparent;")

    badge = QLabel("COMING SOON")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge_font = QFont("Segoe UI", 8)
    badge_font.setWeight(QFont.Weight.DemiBold)
    badge_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
    badge.setFont(badge_font)
    badge.setStyleSheet(f"color: {Tok.ACCENT.name()}; background: transparent;")

    layout.addStretch()
    layout.addWidget(icon_lbl)
    layout.addWidget(title_lbl)
    layout.addSpacing(4)
    layout.addWidget(desc_lbl)
    layout.addSpacing(8)
    layout.addWidget(badge)
    layout.addStretch()
    return w


class CreateView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 32)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────────────────
        header = SectionHeader(
            "✨  Create",
            "Build your world with AI-powered tools.",
        )
        layout.addWidget(header)

        # ── Sub-tabs ──────────────────────────────────────────────────────
        self.subtabs = QTabWidget()

        # Random Generator — fully implemented
        self.random_view = RandomGeneratorView(self.subtabs, config)
        self.subtabs.addTab(self.random_view, "🎲  Random Generator")

        # Map Maker — stub
        self.subtabs.addTab(
            _make_placeholder(
                "🗺️",
                "Map Maker",
                "Draw and annotate campaign maps, pin locations,\nand link places to your lore notes.",
            ),
            "🗺️  Map Maker",
        )

        # NPC Builder — stub
        self.subtabs.addTab(
            _make_placeholder(
                "👤",
                "NPC Builder",
                "Generate detailed non-player characters with AI,\ncomplete with backstory, traits, and stat blocks.",
            ),
            "👤  NPC Builder",
        )

        # Quest Designer — stub
        self.subtabs.addTab(
            _make_placeholder(
                "⚔️",
                "Quest Designer",
                "Design quests, side-missions, and encounter hooks\nwith branching outcomes and reward tables.",
            ),
            "⚔️  Quest Designer",
        )

        layout.addWidget(self.subtabs, 1)
