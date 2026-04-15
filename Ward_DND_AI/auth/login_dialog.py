"""
LoginDialog — PyQt6 login dialog for Ward DND AI.

Displays an authentication UI on app startup. Users enter email (username)
and password. On successful login, the dialog accepts and exposes the User
object. On failure, an inline error message is shown and the dialog remains open.

Password verification uses bcrypt to compare the entered password with the
stored password_hash in the database.

Usage
-----
    from Ward_DND_AI.auth.login_dialog import LoginDialog
    from Ward_DND_AI.storage.sqlite_backend import SQLiteBackend

    storage = SQLiteBackend("ward_dnd.db")
    dialog = LoginDialog(storage)

    if dialog.exec() == QDialog.Accepted:
        current_user = dialog.user
    else:
        # User cancelled login
        pass
"""

from typing import Optional

import bcrypt
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from Ward_DND_AI.models.user import User
from Ward_DND_AI.storage.storage_base import StorageBackend


class LoginDialog(QDialog):
    """
    PyQt6 login dialog for Ward DND AI authentication.

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

    def __init__(self, storage: StorageBackend, parent=None):
        """Initialize the login dialog."""
        super().__init__(parent)
        self.storage = storage
        self.user: Optional[User] = None

        self.setWindowTitle("Ward DND AI — Login")
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
        title_label = QLabel("Ward DND AI")
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

        self.setLayout(layout)

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
