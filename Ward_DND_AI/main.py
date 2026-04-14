#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

# ─── Ensure project root (parent of Ward_DND_AI) is on PYTHONPATH ───
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication

from Ward_DND_AI.ai.core.model_router import get_model_backend
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
    logger.info("Launching Obsidian Lore Assistant...")

    vault_path = Path(config.VAULT_PATH).resolve()
    api_key = config.OPENAI_API_KEY

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault path does not exist: {vault_path}")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in Config")

    ctx = AppContext(config)
    ai_engine = get_model_backend(config, storage=ctx.storage)
    ctx.ai = ai_engine  # wire AI into context

    qapp = QApplication(sys.argv)
    window = LoreMainApp(ctx=ctx)
    window.show()

    logger.info("Application exited cleanly.")
    sys.exit(qapp.exec())


if __name__ == "__main__":
    main()
