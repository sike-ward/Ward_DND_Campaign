"""
LoginDialog — PyQt6 login dialog for MythosEngine.

Displays an authentication UI on app startup. Users enter email (username)
and password. On successful login, the dialog accepts and exposes the User
object. On failure, an inline error message is shown and the dialog remains open.

Password verification uses bcrypt to compare the entered password with the
stored password_hash in the database.

Usage
-----
    from MythosEngine.auth.login_dialog import LoginDialog
    from MythosEngine.storage.sqlite_backend import SQLiteBackend

    storage = SQLiteBackend("mythos_engine.db")
    dialog = LoginDialog(storage)

    if dialog.exec() == QDialog.Accepted:
        current_user = dialog.user
    else:
        # User cancelled login
        pass
"""

import os
from typing import Optional

import bcrypt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from MythosEngine.models.user import User
from MythosEngine.storage.storage_base import StorageBackend

# Injected after AppContext is constructed so LoginDialog can open SignupDialog.
# Set by main.py: LoginDialog.invite_mgr = ctx.invites
# Set by main.py: LoginDialog.user_mgr   = ctx.users
_invite_mgr = None
_user_mgr = None


class LoginDialog(QDialog):
    """
    PyQt6 login dialog for MythosEngine authentication.

    Shows username (email) and password fields. On successful login,
    stores the User object in self.user and accepts the dialog.
    On failure, shows an error message and allows retry.

    Parameters
    ----------
    storage : StorageBackend
        Storage backend used to look up users by email.
    parent : QWidget, optional
        Parent widget (usually None for top-level dialog).
    """

    def __init__(self, storage: StorageBackend, invite_mgr=None, user_mgr=None, parent=None):
        """Initialize the login dialog."""
        super().__init__(parent)
        self.storage = storage
        self._invite_mgr = invite_mgr
        self._user_mgr = user_mgr
        self.user: Optional[User] = None

        self.setWindowTitle("MythosEngine — Login")
        self.setModal(True)
        self.setMinimumWidth(350)

        # Apply dark styling
        self.setStyleSheet(self._get_stylesheet())

        # Build layout
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the UI elements."""
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("MythosEngine")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title_label)

        subtitle = QLabel("Campaign Management & AI Assistant")
        subtitle.setStyleSheet("font-size: 12px; color: #b0b0b0; margin-bottom: 16px;")
        layout.addWidget(subtitle)

        # Username (email) field
        username_label = QLabel("Email:")
        username_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("your@email.com")
        self.username_input.setStyleSheet(self._input_stylesheet())
        self.username_input.returnPressed.connect(self._on_login_clicked)
        layout.addWidget(self.username_input)

        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self._input_stylesheet())
        self.password_input.returnPressed.connect(self._on_login_clicked)
        layout.addWidget(self.password_input)

        # Error message label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)

        login_button = QPushButton("Login")
        login_button.setStyleSheet(self._button_stylesheet())
        login_button.setMinimumHeight(40)
        login_button.clicked.connect(self._on_login_clicked)
        button_layout.addWidget(login_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(self._cancel_button_stylesheet())
        cancel_button.setMinimumHeight(40)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addSpacing(8)
        layout.addLayout(button_layout)

        # Signup link — only shown when invite infrastructure is available
        if self._invite_mgr and self._user_mgr:
            signup_btn = QPushButton("Don't have an account?  Sign Up with Invite Code")
            signup_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #8B5CF6; "
                "border: none; font-size: 10px; text-decoration: underline; }"
                "QPushButton:hover { color: #7C3AED; }"
            )
            signup_btn.setCursor(__import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.CursorShape.PointingHandCursor)
            signup_btn.clicked.connect(self._on_signup)
            layout.addWidget(signup_btn)

        # Dev quick-login panel — only rendered when DEV_MODE=true
        if os.environ.get("DEV_MODE", "").lower() == "true":
            self._build_dev_panel(layout)

        self.setLayout(layout)

    def _build_dev_panel(self, layout: QVBoxLayout) -> None:
        """Append a collapsible dev-only quick-login section to layout."""
        layout.addSpacing(8)

        toggle_btn = QPushButton("▶  Dev Quick Login")
        toggle_btn.setCheckable(True)
        toggle_btn.setStyleSheet(
            "QPushButton { background-color: #3d2000; color: #ffaa00; "
            "border: 1px solid #ffaa00; border-radius: 4px; font-size: 11px; "
            "padding: 6px 10px; text-align: left; font-weight: bold; }"
            "QPushButton:checked { background-color: #4d2c00; }"
            "QPushButton:hover { background-color: #4d2c00; }"
        )
        layout.addWidget(toggle_btn)

        dev_frame = QFrame()
        dev_frame.setStyleSheet(
            "QFrame { background-color: #2a1500; border: 1px solid #ffaa00; "
            "border-radius: 4px; }"
        )
        dev_frame.setVisible(False)

        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(12, 10, 12, 12)
        frame_layout.setSpacing(8)

        warning = QLabel("⚠  Dev mode — do not use in production")
        warning.setStyleSheet("color: #ffaa00; font-size: 11px; font-style: italic;")
        frame_layout.addWidget(warning)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        dm_btn = QPushButton("Login as DM")
        dm_btn.setStyleSheet(
            "QPushButton { background-color: #5c3a00; color: #ffcc44; "
            "border: 1px solid #ffaa00; border-radius: 4px; "
            "font-size: 12px; font-weight: bold; padding: 6px; }"
            "QPushButton:hover { background-color: #7a4d00; }"
            "QPushButton:pressed { background-color: #3d2600; }"
        )
        dm_btn.setMinimumHeight(36)
        dm_btn.clicked.connect(lambda: self._dev_login("dm_test@dev.local", "devtest"))
        btn_row.addWidget(dm_btn)

        player_btn = QPushButton("Login as Player")
        player_btn.setStyleSheet(
            "QPushButton { background-color: #003a3a; color: #44eeff; "
            "border: 1px solid #00dddd; border-radius: 4px; "
            "font-size: 12px; font-weight: bold; padding: 6px; }"
            "QPushButton:hover { background-color: #004d4d; }"
            "QPushButton:pressed { background-color: #002626; }"
        )
        player_btn.setMinimumHeight(36)
        player_btn.clicked.connect(lambda: self._dev_login("player_test@dev.local", "devtest"))
        btn_row.addWidget(player_btn)

        frame_layout.addLayout(btn_row)
        dev_frame.setLayout(frame_layout)
        layout.addWidget(dev_frame)

        def _on_toggle(checked: bool) -> None:
            dev_frame.setVisible(checked)
            toggle_btn.setText("▼  Dev Quick Login" if checked else "▶  Dev Quick Login")

        toggle_btn.toggled.connect(_on_toggle)

    def _dev_login(self, email: str, password: str) -> None:
        """Fill in credentials and trigger login for dev quick-login buttons."""
        self.username_input.setText(email)
        self.password_input.setText(password)
        self._on_login_clicked()

    def _on_login_clicked(self) -> None:
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Validate input
        if not username or not password:
            self._show_error("Please enter both email and password.")
            return

        # Attempt authentication
        user = self.authenticate(username, password, self.storage)
        if user:
            self.user = user
            self.accept()
        else:
            self._show_error("Invalid email or password. Please try again.")
            self.password_input.clear()
            self.password_input.setFocus()

    def _on_signup(self) -> None:
        """Open the signup dialog. On success, treat new account as the logged-in user."""
        from MythosEngine.auth.signup_dialog import SignupDialog

        dlg = SignupDialog(
            storage=self.storage,
            invite_mgr=self._invite_mgr,
            user_mgr=self._user_mgr,
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.user:
            self.user = dlg.user
            self.accept()

    def _show_error(self, message: str) -> None:
        """Display an error message."""
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    @staticmethod
    def authenticate(username: str, password: str, storage: StorageBackend) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Parameters
        ----------
        username : str
            User's email address.
        password : str
            User's plaintext password (not hashed).
        storage : StorageBackend
            Storage backend to look up the user.

        Returns
        -------
        User | None
            The authenticated User object, or None if authentication failed.
        """
        # Look up user by email
        user = storage.get_user_by_email(username)
        if not user:
            return None

        # Verify password using bcrypt
        try:
            password_bytes = password.encode("utf-8")
            hash_bytes = user.password_hash.encode("utf-8")
            if bcrypt.checkpw(password_bytes, hash_bytes):
                return user
        except Exception:
            # bcrypt validation error — treat as auth failure
            pass

        return None

    # ========================================================================
    # Styling
    # ========================================================================

    def _get_stylesheet(self) -> str:
        """Return the main dialog stylesheet."""
        return """
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        """

    def _input_stylesheet(self) -> str:
        """Return the stylesheet for input fields."""
        return """
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #4a9eff;
                background-color: #333333;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """

    def _button_stylesheet(self) -> str:
        """Return the stylesheet for the login button."""
        return """
            QPushButton {
                background-color: #4a9eff;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5b8fff;
            }
            QPushButton:pressed {
                background-color: #3d7acc;
            }
        """

    def _cancel_button_stylesheet(self) -> str:
        """Return the stylesheet for the cancel button."""
        return """
            QPushButton {
                background-color: #3d3d3d;
                color: #b0b0b0;
                border: 1px solid #505050;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #454545;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """
