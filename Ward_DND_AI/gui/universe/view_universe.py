from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class UniverseView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Header
        self.header_label = QLabel("Universe Timeline")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Event list
        self.event_list = QTextEdit()
        self.event_list.setReadOnly(True)
        layout.addWidget(self.event_list, 1)

        # Buttons row
        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)

        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.delete_btn)
