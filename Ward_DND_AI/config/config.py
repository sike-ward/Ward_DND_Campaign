import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "settings.json"


class Config:
    # Default values
    VAULT_PATH = r"C:\Users\Evan\Desktop\Ward_DND_Campaign"
    OPENAI_API_KEY = ""
    MODEL = "gpt-3.5"
    LOG_PATH = r"C:\Users\Evan\Desktop\Ward_DND_Campaign\app.log"
    LOG_LEVEL = logging.INFO

    @classmethod
    def load(cls):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls.VAULT_PATH = data.get("vault_path", cls.VAULT_PATH)
                    cls.OPENAI_API_KEY = data.get("openai_api_key", cls.OPENAI_API_KEY)
                    cls.MODEL = data.get("v0", cls.MODEL)
                    level_str = data.get("0", "INFO").upper()
                    cls.LOG_LEVEL = getattr(logging, level_str, logging.INFO)

            except Exception as e:
                log_warning(f"Failed to load config: {e}")

    @classmethod
    def save(cls):
        data = {
            "vault_path": cls.VAULT_PATH,
            "openai_api_key": cls.OPENAI_API_KEY,
            "model": cls.MODEL,
        }
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            log_warning(f"Failed to save config: {e}")

    @staticmethod
    def setup_logging():
        log_dir = Path(Config.LOG_PATH).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            Config.LOG_PATH, maxBytes=5_000_000, backupCount=5, encoding="utf-8"
        )
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(Config.LOG_LEVEL)

        # Prevent duplicate handlers
        if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
            root_logger.addHandler(handler)

        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


# --- Logging Shortcuts ---
def log_info(msg):
    logging.info(msg)


def log_warning(msg):
    logging.warning(msg)


def log_error(msg):
    logging.error(msg)


def log_exception(message, exception):
    logging.exception(f"{message} | {exception}")
