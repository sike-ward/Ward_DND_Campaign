"""
Account Settings controller — wires the password-change form to UserManager.

Available to every logged-in user.
"""

from MythosEngine.gui.settings.account.view_account import AccountSettingsView


class AccountSettingsController:
    """Manages the My Account panel — account info + self-service password change."""

    def __init__(self, view: AccountSettingsView, ctx):
        self.view = view
        self.ctx = ctx

        # Populate account info
        self._populate_info()

        # Connect save button
        view.btn_save.clicked.connect(self._on_change_password)

        # Allow Enter in confirm field to submit
        view.confirm_pw.returnPressed.connect(self._on_change_password)

    def _populate_info(self):
        user = self.ctx.current_user
        if user is None:
            return
        self.view.lbl_username.setText(user.username)
        self.view.lbl_email.setText(user.email)
        self.view.lbl_role.setText(", ".join(user.roles) if user.roles else "player")

    def _on_change_password(self):
        current = self.view.current_pw.text()
        new_pw = self.view.new_pw.text()
        confirm = self.view.confirm_pw.text()

        # ── Quick UI-side validation ──────────────────────────────────
        if not current:
            self.view.show_status("Please enter your current password.", error=True)
            return
        if len(new_pw) < 8:
            self.view.show_status("New password must be at least 8 characters.", error=True)
            return
        if new_pw != confirm:
            self.view.show_status("New passwords do not match.", error=True)
            return

        user = self.ctx.current_user
        if user is None:
            self.view.show_status("No active user session.", error=True)
            return

        # ── Delegate to UserManager (verifies current pw & applies new) ──
        try:
            self.ctx.users.change_password(user.id, current, new_pw)
            self.view.clear_password_fields()
            self.view.show_status("Password updated successfully.")
        except ValueError as exc:
            self.view.show_status(str(exc), error=True)
        except Exception as exc:
            self.view.show_status(f"Failed to update password: {exc}", error=True)
