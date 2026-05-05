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
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        self.header_label = QLabel("Universe Timeline")
        self.header_label.setStyleSheet("font-size: 22pt; font-weight: 700; background: transparent;")
        layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Event list
        self.event_list = QTextEdit()
        self.event_list.setReadOnly(True)
        self.event_list.setProperty("readonly", "true")
        layout.addWidget(self.event_list, 1)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.add_btn = QPushButton("Add")
        self.add_btn.setMinimumHeight(36)
        self.add_btn.setFixedWidth(100)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setProperty("secondary", "true")
        self.edit_btn.setMinimumHeight(36)
        self.edit_btn.setFixedWidth(100)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setProperty("danger", "true")
        self.delete_btn.setMinimumHeight(36)
        self.delete_btn.setFixedWidth(100)

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
