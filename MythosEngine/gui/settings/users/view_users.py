"""
Admin Panel — tabbed view for administrators.

Tabs:
  0  Users          — create, reset password, enable/disable accounts
  1  Invite Codes   — generate, copy, and revoke invite codes
  2  Active Sessions — view and revoke live sessions

Only visible / functional when logged in as an admin.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import GlowButton, SectionHeader

# ── Tab indices ────────────────────────────────────────────────────────────────
TAB_USERS = 0
TAB_INVITES = 1
TAB_SESSIONS = 2


def _setup_modern_table(table: QTableWidget, row_height: int = 48):
    """Apply consistent modern styling to a QTableWidget."""
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setShowGrid(False)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(row_height)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    # Ensure horizontal header stretches nicely
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setMinimumHeight(40)


# ── Users tab ─────────────────────────────────────────────────────────────────


class UsersTab(QWidget):
    """User account management table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(14)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.btn_create = GlowButton("✚  Create Account", "primary")
        self.btn_create.setFixedWidth(175)
        self.btn_create.setMinimumHeight(38)
        self.btn_refresh = GlowButton("↻  Refresh", "secondary")
        self.btn_refresh.setFixedWidth(105)
        self.btn_refresh.setMinimumHeight(38)
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
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 310)
        _setup_modern_table(self.table, row_height=50)
        layout.addWidget(self.table)

        self.status_label = QLabel("")
        self.status_label.setProperty("role", "muted")
        layout.addWidget(self.status_label)

    def show_status(self, msg: str, error: bool = False):
        color = "#EF4444" if error else "#10B981"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 9pt; background: transparent;")
        self.status_label.setText(msg)


# ── Invite Codes tab ──────────────────────────────────────────────────────────


class InviteCodesTab(QWidget):
    """Invite code generation and management."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(14)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.btn_generate = GlowButton("✚  Generate New Code", "primary")
        self.btn_generate.setFixedWidth(195)
        self.btn_generate.setMinimumHeight(38)
        self.btn_refresh = GlowButton("↻  Refresh", "secondary")
        self.btn_refresh.setFixedWidth(105)
        self.btn_refresh.setMinimumHeight(38)
        toolbar.addWidget(self.btn_generate)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Code", "Created By", "Created", "Expires", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 140)
        _setup_modern_table(self.table, row_height=48)
        layout.addWidget(self.table)

        self.status_label = QLabel("")
        self.status_label.setProperty("role", "muted")
        layout.addWidget(self.status_label)

    def show_status(self, msg: str, error: bool = False):
        color = "#EF4444" if error else "#10B981"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 9pt; background: transparent;")
        self.status_label.setText(msg)


# ── Active Sessions tab ───────────────────────────────────────────────────────


class ActiveSessionsTab(QWidget):
    """Live session viewer and revoke panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(14)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.btn_refresh = GlowButton("↻  Refresh", "secondary")
        self.btn_refresh.setFixedWidth(105)
        self.btn_refresh.setMinimumHeight(38)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["User", "Started", "Expires", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 140)
        _setup_modern_table(self.table, row_height=48)
        layout.addWidget(self.table)

        self.status_label = QLabel("")
        self.status_label.setProperty("role", "muted")
        layout.addWidget(self.status_label)

    def show_status(self, msg: str, error: bool = False):
        color = "#EF4444" if error else "#10B981"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 9pt; background: transparent;")
        self.status_label.setText(msg)


# ── Admin Panel (top-level, wraps all tabs) ───────────────────────────────────


class UserManagementView(QWidget):
    """
    Admin Panel — container with Users / Invite Codes / Active Sessions tabs.

    The class is named UserManagementView for backward compatibility with
    view_settings.py and controller_settings.py.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header = SectionHeader(
            "🛡️  Admin Panel",
            "Manage users, invite codes, and active sessions.",
        )
        layout.addWidget(header)

        # Tabbed content
        self.tabs = QTabWidget()
        self.users_tab = UsersTab(self.tabs)
        self.invites_tab = InviteCodesTab(self.tabs)
        self.sessions_tab = ActiveSessionsTab(self.tabs)

        self.tabs.addTab(self.users_tab, "👥  Users")
        self.tabs.addTab(self.invites_tab, "🎟️  Invite Codes")
        self.tabs.addTab(self.sessions_tab, "🔑  Active Sessions")
        layout.addWidget(self.tabs, 1)

    # ── Back-compat shims so existing controller code still works ──────────────

    @property
    def table(self):
        return self.users_tab.table

    @property
    def btn_create(self):
        return self.users_tab.btn_create

    @property
    def btn_refresh(self):
        return self.users_tab.btn_refresh

    def show_status(self, msg: str, error: bool = False):
        self.users_tab.show_status(msg, error=error)


# ── CreateUserDialog ──────────────────────────────────────────────────────────


class CreateUserDialog(QDialog):
    """Dialog for creating a new user account (admin-initiated)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")
        self.setMinimumWidth(420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(12)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@example.com")
        self.email_input.setMinimumHeight(36)
        form.addRow("Email:", self.email_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Display name")
        self.username_input.setMinimumHeight(36)
        form.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Minimum 8 characters")
        self.password_input.setMinimumHeight(36)
        form.addRow("Password:", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["player", "gm", "admin"])
        self.role_combo.setMinimumHeight(36)
        form.addRow("Role:", self.role_combo)

        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF4444; background: transparent;")
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
