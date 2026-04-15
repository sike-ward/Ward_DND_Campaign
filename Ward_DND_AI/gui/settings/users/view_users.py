"""
User Management view — admin-only panel for creating and managing accounts.
Only visible/functional when logged in as an admin.
"""

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class UserManagementView(QWidget):
    """Admin panel for viewing and managing user accounts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("User Management")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Create and manage accounts. Admin access only.")
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)

        toolbar = QHBoxLayout()
        self.btn_create = QPushButton("+ Create Account")
        self.btn_create.setFixedWidth(160)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setFixedWidth(100)
        toolbar.addWidget(self.btn_create)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 140)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(self.status_label)

    def show_status(self, msg: str, error: bool = False):
        color = "#e74c3c" if error else "#2ecc71"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 9pt;")
        self.status_label.setText(msg)


class CreateUserDialog(QDialog):
    """Dialog for creating a new user account."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")
        self.setMinimumWidth(380)
        self.setModal(True)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@example.com")
        form.addRow("Email:", self.email_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Display name")
        form.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Minimum 8 characters")
        form.addRow("Password:", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["player", "admin"])
        form.addRow("Role:", self.role_combo)

        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if not self.email_input.text().strip() or "@" not in self.email_input.text():
            self.error_label.setText("Please enter a valid email address.")
            return
        if not self.username_input.text().strip():
            self.error_label.setText("Username is required.")
            return
        if len(self.password_input.text()) < 8:
            self.error_label.setText("Password must be at least 8 characters.")
            return
        self.accept()

    @property
    def email(self):
        return self.email_input.text().strip()

    @property
    def username(self):
        return self.username_input.text().strip()

    @property
    def password(self):
        return self.password_input.text()

    @property
    def role(self):
        return self.role_combo.currentText()
