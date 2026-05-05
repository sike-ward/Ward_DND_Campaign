from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.settings.help.debug.view_debug import DebugView
from MythosEngine.gui.widgets import GlowButton, SectionHeader


class HelpView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 32)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────────────────────
        header = SectionHeader("❓  Help & About", "Documentation, debug logs, and contact information.")
        layout.addWidget(header)

        # ── Tabs ─────────────────────────────────────────────────────────────
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs, 1)

        # --- Documentation Tab ---
        doc_tab = QWidget()
        doc_layout = QVBoxLayout(doc_tab)
        doc_layout.setContentsMargins(16, 16, 16, 16)
        doc_layout.setSpacing(12)

        self.help_textbox = QTextEdit()
        self.help_textbox.setReadOnly(True)
        self.help_textbox.setProperty("readonly", "true")
        doc_layout.addWidget(self.help_textbox)

        footer_row = QHBoxLayout()
        self.link_button = GlowButton("📖  Open Full Documentation", "secondary")
        self.link_button.setMinimumHeight(36)
        self.link_button.setFixedWidth(230)
        self.link_button.clicked.connect(self.open_docs_clicked)
        footer_row.addWidget(self.link_button)
        footer_row.addStretch()

        contact = QLabel("Contact: wardloredev@gmail.com")
        contact.setProperty("role", "muted")
        contact.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        footer_row.addWidget(contact)
        doc_layout.addLayout(footer_row)

        self.tabs.addTab(doc_tab, "Help")

        # --- Debug/Log Tab ---
        self.debug_view = DebugView(self)
        self.tabs.addTab(self.debug_view, "Debug / Logs")

    def set_text(self, content):
        self.help_textbox.setPlainText(content)

    def open_docs_clicked(self):
        pass  # Controller wires this
