from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SummarizeView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Summarize Tab")
        title.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(QLabel("Choose a folder to summarize:"))

        self.folder_menu = QComboBox()
        layout.addWidget(self.folder_menu)

        layout.addWidget(QLabel("Choose a summary style:"))

        self.style_menu = QComboBox()
        self.style_menu.addItems(["brief", "detailed", "narrative"])
        self.style_menu.setCurrentText("brief")
        layout.addWidget(self.style_menu)

        self.summarize_btn = QPushButton("Summarize")
        layout.addWidget(self.summarize_btn)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setAcceptRichText(False)
        layout.addWidget(self.output_text, 1)

    def set_output(self, text: str):
        self.output_text.setPlainText(text)
