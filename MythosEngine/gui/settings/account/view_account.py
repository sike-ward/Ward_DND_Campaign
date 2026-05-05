"""
Account Settings view — self-service password change and account info.

Available to every logged-in user (not just admins).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import GlowButton, SectionHeader


class AccountSettingsView(QWidget):
    """
    My Account panel — shows basic account info and a password-change form.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 32)
        layout.setSpacing(24)

        # ── Header ────────────────────────────────────────────────────────
        header = SectionHeader("My Account", "View your account details and change your password.")
        layout.addWidget(header)

        # ── Account info (read-only) ─────────────────────────────────────
        info_group = QGroupBox("Account Info")
        info_layout = QFormLayout()
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(16, 16, 16, 16)

        self.lbl_username = QLabel("—")
        self.lbl_username.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addRow("Username:", self.lbl_username)

        self.lbl_email = QLabel("—")
        self.lbl_email.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addRow("Email:", self.lbl_email)

        self.lbl_role = QLabel("—")
        info_layout.addRow("Role:", self.lbl_role)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # ── Change Password ──────────────────────────────────────────────
        pw_group = QGroupBox("Change Password")
        pw_layout = QFormLayout()
        pw_layout.setSpacing(12)
        pw_layout.setContentsMargins(16, 16, 16, 16)

        self.current_pw = QLineEdit()
        self.current_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_pw.setPlaceholderText("Enter your current password")
        self.current_pw.setMaximumWidth(320)
        self.current_pw.setMinimumHeight(40)
        pw_layout.addRow("Current password:", self.current_pw)

        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pw.setPlaceholderText("Minimum 8 characters")
        self.new_pw.setMaximumWidth(320)
        self.new_pw.setMinimumHeight(40)
        pw_layout.addRow("New password:", self.new_pw)

        self.confirm_pw = QLineEdit()
        self.confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pw.setPlaceholderText("Repeat new password")
        self.confirm_pw.setMaximumWidth(320)
        self.confirm_pw.setMinimumHeight(40)
        pw_layout.addRow("Confirm:", self.confirm_pw)

        pw_group.setLayout(pw_layout)
        layout.addWidget(pw_group)

        # ── Action row ───────────────────────────────────────────────────
        action_row = QHBoxLayout()
        self.btn_save = GlowButton("Update Password", "success")
        self.btn_save.setFixedHeight(38)
        self.btn_save.setFixedWidth(185)
        action_row.addWidget(self.btn_save)
        action_row.addStretch()
        layout.addLayout(action_row)

        # ── Status message ───────────────────────────────────────────────
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setProperty("role", "muted")
        layout.addWidget(self.status_label)

        layout.addStretch()

    # ── Helpers ───────────────────────────────────────────────────────────

    def show_status(self, msg: str, error: bool = False):
        color = "#EF4444" if error else "#10B981"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 9pt; background: transparent;")
        self.status_label.setText(msg)

    def clear_password_fields(self):
        self.current_pw.clear()
        self.new_pw.clear()
        self.confirm_pw.clear()
