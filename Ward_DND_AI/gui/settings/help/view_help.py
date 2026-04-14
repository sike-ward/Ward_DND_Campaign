from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from Ward_DND_AI.gui.settings.help.debug.view_debug import (
    DebugView,
)


class HelpView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs, 1)

        # --- Documentation Tab ---
        doc_tab = QWidget()
        doc_layout = QVBoxLayout(doc_tab)
        doc_layout.setContentsMargins(12, 12, 12, 12)
        doc_layout.setSpacing(8)

        title = QLabel("Help & Documentation")
        title.setStyleSheet("font-weight: bold; font-size: 16pt;")
        doc_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        self.help_textbox = QTextEdit()
        self.help_textbox.setReadOnly(True)
        doc_layout.addWidget(self.help_textbox)

        self.link_button = QPushButton("📖 Open Full Documentation")
        doc_layout.addWidget(self.link_button, alignment=Qt.AlignmentFlag.AlignLeft)

        contact_label = QLabel("Contact: wardloredev@gmail.com")
        contact_label.setStyleSheet("color: gray;")
        doc_layout.addWidget(contact_label, alignment=Qt.AlignmentFlag.AlignLeft)

        self.tabs.addTab(doc_tab, "Help")

        # --- Debug/Log Tab ---
        self.debug_view = DebugView(self)
        self.tabs.addTab(self.debug_view, "Debug / Logs")

        # Expose buttons for controller wiring
        # (Signals will be handled in controller)
        self.link_button.clicked.connect(self.open_docs_clicked)

    def set_text(self, content):
        self.help_textbox.setPlainText(content)

    # --- Controller will connect this slot ---
    def open_docs_clicked(self):
        pass  # Controller wires this

    # Add passthroughs for debug_view as needed, or access via .debug_view
