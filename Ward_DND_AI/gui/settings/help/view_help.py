from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget


class HelpView(QWidget):
    open_docs_clicked = pyqtSignal()

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Help & Documentation")
        title.setStyleSheet("font-weight: bold; font-size: 16pt;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        self.help_textbox = QTextEdit()
        self.help_textbox.setReadOnly(True)
        layout.addWidget(self.help_textbox)

        self.link_button = QPushButton("📖 Open Full Documentation")
        layout.addWidget(self.link_button, alignment=Qt.AlignmentFlag.AlignLeft)

        contact_label = QLabel("Contact: wardloredev@gmail.com")
        contact_label.setStyleSheet("color: gray;")
        layout.addWidget(contact_label, alignment=Qt.AlignmentFlag.AlignLeft)

        self.link_button.clicked.connect(self.open_docs_clicked.emit)

    def set_text(self, content):
        self.help_textbox.setPlainText(content)
