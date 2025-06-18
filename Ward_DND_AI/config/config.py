import json
import logging
import os
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "settings.json"
DEFAULT_CONFIG = {
    "VAULT_PATH": "./Obsidian",
    "VAULT_TYPE": "obsidian",
    "OPENAI_API_KEY": "",
    "EMBEDDING_MODEL": "text-embedding-3-small",
    "COMPLETION_MODEL": "gpt-4o",
    "MAX_TOKENS": 4000,
    "LOG_FILE": "logs/app.log",
    "LOG_LEVEL": "INFO",
    "AUTO_REFRESH_INTERVAL": 300,
    "ENABLE_EXPERIMENTAL": False,
    "AI_BACKENDS": {"ask": "openai", "summarize": "openai", "search": "openai"},
}


class Config:
    def __init__(self):
        self._path = Path(__file__).parent / "settings.json"

        print(">>> [config] Will load from:", self._path)
        print(
            ">>> [DEBUG] Files in config dir:",
            list(Path(__file__).parent.parent.parent.glob("*")),
        )

        self._data = DEFAULT_CONFIG.copy()
        self._load()
        self._init_logger()

    def _load(self):
        print(">>> [config] Loading settings from:", self._path)
        if self._path.exists():
            try:
                with self._path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                print(">>> [config] Loaded raw JSON:", raw)
                self._data.clear()
                for key in DEFAULT_CONFIG:
                    val = raw.get(key, DEFAULT_CONFIG[key])
                    env_val = os.getenv(key)
                    if env_val is not None:
                        val = self._cast_value(env_val, DEFAULT_CONFIG[key])
                    self._data[key] = val
            except Exception as e:
                print(f"[config] Failed to load or parse config file: {e}")
                self._data = DEFAULT_CONFIG.copy()
        else:
            print(">>> [config] settings.json file not found.")
            self._data = DEFAULT_CONFIG.copy()

    def _cast_value(self, val: str, default: Any) -> Any:
        if isinstance(default, bool):
            return val.lower() in ("1", "true", "yes")
        if isinstance(default, int):
            return int(val)
        return val

    def save(self):
        try:
            with self._path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            self.log_info("Settings saved.")
        except Exception as e:
            self.log_error(f"Failed to save config: {e}")

    def _init_logger(self):
        self.logger = logging.getLogger("LoreLogger")
        self.logger.setLevel(logging.DEBUG)

        log_file = self._data.get("LOG_FILE", "logs/app.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(message)s"))
        ch.setLevel(logging.INFO)

        self.logger.handlers.clear()
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    # Logging shortcuts
    def log_info(self, msg):
        self.logger.info(msg)

    def log_warn(self, msg):
        self.logger.warning(msg)

    def log_error(self, msg):
        self.logger.error(msg)

    def reload(self):
        self._load()
        self._init_logger()

    # Property access
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Config has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in ("_path", "_data", "logger"):
            super().__setattr__(name, value)
        elif name in DEFAULT_CONFIG:
            self._data[name] = value
            self.save()
        else:
            raise AttributeError(f"Cannot set unknown config field '{name}'")

    def get(self, key, default=None):
        return self._data.get(key, default)


def log_exception(e: Exception, context: str = ""):
    err_msg = f"Unhandled exception: {e}\n{traceback.format_exc()}"
    print(f"[ERROR] {context} - {err_msg}")
