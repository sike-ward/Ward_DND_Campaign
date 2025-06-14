import importlib

from Ward_DND_AI.config.config import Config


class StorageRouter:
    def __init__(self, config: Config):
        self._config = config
        self.backend = self._load_backend()

    def _load_backend(self):
        storage_type = self._config.VAULT_TYPE.lower()

        module_name = f"Ward_DND_AI.storage.{storage_type}_backend"
        class_name = f"{storage_type.capitalize()}Storage"

        try:
            module = importlib.import_module(module_name)
            backend_class = getattr(module, class_name)
            return backend_class(self._config.VAULT_PATH)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(
                f"Storage type '{storage_type}' is not supported or misconfigured. ({e})"
            )

    def __getattr__(self, attr):
        return getattr(self.backend, attr)


def get_storage_backend(storage_type: str, vault_path: str):
    from Ward_DND_AI.config.config import Config

    Config.VAULT_TYPE = storage_type
    Config.VAULT_PATH = vault_path
    return StorageRouter(Config()).backend
