# MythosEngine/gui/universe/timeline/view_timeline.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import GlowButton, SectionHeader


class TimelineView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 32)
        root.setSpacing(20)

        # Header row
        header_row = QHBoxLayout()
        header = SectionHeader(
            "\U0001f30c  Universe Timeline",
            "Track events, story arcs, and history across your world.",
        )
        header_row.addWidget(header)
        header_row.addStretch()

        self.add_btn = GlowButton("+ Add Event", "primary")
        self.add_btn.setFixedWidth(145)
        self.add_btn.setMinimumHeight(38)
        header_row.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        root.addLayout(header_row)

        # Timeline area
        self.event_list = QTextEdit()
        self.event_list.setReadOnly(True)
        self.event_list.setAcceptRichText(False)
        self.event_list.setProperty("readonly", "true")
        self.event_list.setPlaceholderText("No timeline events yet. Click + Add Event to get started.")
        root.addWidget(self.event_list, 1)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.edit_btn = GlowButton("Edit", "secondary")
        self.delete_btn = GlowButton("Delete", "danger")

        for btn in (self.edit_btn, self.delete_btn):
            btn.setFixedWidth(105)
            btn.setMinimumHeight(38)
            btn_row.addWidget(btn)

        btn_row.addStretch()
        root.addLayout(btn_row)
