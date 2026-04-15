#!/usr/bin/env python3
"""
Ward DND AI — Application entry point.

Launch order:
  1. Load config + logging
  2. Initialise AppContext (SQLite storage, managers, permissions)
  3. Bootstrap admin account on first launch
  4. Show login dialog — app exits if cancelled
  5. Wire AI engine
  6. Open main window
"""

import logging
import sys
from pathlib import Path

# Ensure project root (parent of Ward_DND_AI) is on PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication

from Ward_DND_AI.ai.core.model_router import get_model_backend
from Ward_DND_AI.auth.login_dialog import LoginDialog
from Ward_DND_AI.config.config import Config
from Ward_DND_AI.context.app_context import AppContext
from Ward_DND_AI.gui.gui import LoreMainApp
from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes


@catch_and_report_crashes
def main():
    config = Config()
    config.log_info("Config loaded and logging initialized.")
    config.reload()

    logger = logging.getLogger(__name__)
    logger.info("Launching Ward DND AI...")

    vault_path = Path(config.VAULT_PATH).resolve()
    api_key = config.OPENAI_API_KEY

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault path does not exist: {vault_path}")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in Config")

    # --- Initialise AppContext (SQLite storage by default) ---
    ctx = AppContext(config)

    # --- Bootstrap admin account on first ever launch ---
    # Credentials are printed to the console once.
    # Change the password from Settings > Account after first login.
    if not ctx.users.get_user_by_email("admin@ward-dnd.local"):
        ctx.users.create_user(
            email="admin@ward-dnd.local",
            username="admin",
            password="WardDND2024!",
            roles=["admin"],
        )
        logger.info("=" * 60)
        logger.info("FIRST LAUNCH — admin account created")
        logger.info("  Email:    admin@ward-dnd.local")
        logger.info("  Password: WardDND2024!")
        logger.info("  Change this password in Settings > Account")
        logger.info("=" * 60)

    # --- PyQt application + login dialog ---
    qapp = QApplication(sys.argv)

    login = LoginDialog(storage=ctx.storage)
    if login.exec() != LoginDialog.DialogCode.Accepted:
        logger.info("Login cancelled — exiting.")
        sys.exit(0)

    ctx.current_user_id = login.user.id
    logger.info("Logged in as: %s (%s)", login.user.username, login.user.id)

    # --- Wire AI engine after login ---
    ai_engine = get_model_backend(config, storage=ctx.storage)
    ctx.ai = ai_engine

    # --- Launch main window ---
    window = LoreMainApp(ctx=ctx)
    window.show()

    logger.info("Application started.")
    sys.exit(qapp.exec())


if __name__ == "__main__":
    main()
