#!/usr/bin/env python3
import sys
from pathlib import Path

# ─── Ensure project root (parent of Ward_DND_AI) is on PYTHONPATH ───
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# ─── Now safe to import local modules ───────────────────────────────
import logging

from PyQt6.QtWidgets import QApplication

from Ward_DND_AI.ai.core.model_router import get_model_backend
from Ward_DND_AI.config.config import Config
from Ward_DND_AI.gui.gui import LoreMainApp
from Ward_DND_AI.storage.storage_router import get_storage_backend


def main():
    try:
        # ─── Logging ───────────────────────────────────────
        print(">>> [main] Starting setup_logging()")
        config = Config()
        config.log_info("Config loaded and logging initialized.")
        config.reload()
        print(">>> DEBUG:", config._data)
        print(">>> OPENAI_API_KEY from config:", config.OPENAI_API_KEY)

        logger = logging.getLogger(__name__)
        logger.info("Launching Obsidian Lore Assistant...")

        # ─── Load settings from JSON ───────────────────────
        print(">>> [main] Resolving paths and config")
        vault_path = Path(config.VAULT_PATH).resolve()
        api_key = config.OPENAI_API_KEY

        if not vault_path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {vault_path}")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in Config")

        # ─── AI and Storage ────────────────────────────────
        print(">>> [main] Initializing AI engine and storage backend")
        storage_backend = get_storage_backend(config)
        ai_engine = get_model_backend(config)

        print(">>> [main] Creating QApplication and LoreMainApp()")
        qapp = QApplication(sys.argv)
        window = LoreMainApp(
            ai_engine=ai_engine, storage_backend=storage_backend, config=config
        )
        window.show()
        print(">>> [main] Entering main loop")
        qapp.exec()
        print(">>> [main] Application exited cleanly")

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        from Ward_DND_AI.utils.crash_handler import handle_crash

        handle_crash(exc_type, exc_value, exc_traceback)
    sys.exit(1)


if __name__ == "__main__":
    main()
