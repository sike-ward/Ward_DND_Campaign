#!/usr/bin/env python3
import sys
from pathlib import Path

# ─── Ensure project root (parent of Ward_DND_AI) is on PYTHONPATH ───
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# ─── Now safe to import local modules ───────────────────────────────
import logging

from Ward_DND_AI.ai.ai_engine import LoreAI
from Ward_DND_AI.config.config import Config
from Ward_DND_AI.gui.gui import LoreMainApp
from Ward_DND_AI.storage.storage_router import get_storage_backend
from Ward_DND_AI.utils.crash_handler import handle_crash


def main():
    try:
        # ─── Logging ───────────────────────────────────────
        print(">>> [main] Starting setup_logging()")
        Config.setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Launching Obsidian Lore Assistant...")

        # ─── Load settings from JSON ───────────────────────
        print(">>> [main] Resolving paths and config")
        Config.load()  # <-- this is the line you were missing

        vault_path = Path(Config.VAULT_PATH).resolve()
        api_key = Config.OPENAI_API_KEY

        if not vault_path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {vault_path}")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in Config")

        # ─── AI and Storage ────────────────────────────────
        print(">>> [main] Initializing AI engine and storage backend")
        ai_engine = LoreAI(vault_path=vault_path, api_key=api_key)
        storage_backend = get_storage_backend("obsidian", vault_path)

        # ─── GUI App ───────────────────────────────────────
        print(">>> [main] Creating LoreMainApp()")
        app = LoreMainApp(ai_engine=ai_engine, storage_backend=storage_backend)
        print(">>> [main] Entering main loop")
        app.mainloop()
        print(">>> [main] Application exited cleanly")

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        handle_crash(exc_type, exc_value, exc_traceback)
        sys.exit(1)


if __name__ == "__main__":
    main()
