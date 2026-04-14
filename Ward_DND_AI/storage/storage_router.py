## Ward_DND_AI/storage/storage_router.py

import importlib

from Ward_DND_AI.storage.storage_base import StorageBackend


class StorageRouter:
    def __init__(self, config):
        self._config = config
        self.backend = self._load_backend()

    def _load_backend(self) -> StorageBackend:
        storage_type = getattr(self._config, "VAULT_TYPE", "").lower()
        vault_path = getattr(self._config, "VAULT_PATH", None)
        if not storage_type or not vault_path:
            raise ValueError("VAULT_TYPE and VAULT_PATH must be set in config.")
        module_name = f"Ward_DND_AI.storage.{storage_type}_storage"
        cls_name = f"{storage_type.capitalize()}Storage"
        try:
            module = importlib.import_module(module_name)
            backend_cls = getattr(module, cls_name)
            instance = backend_cls(vault_path)
            if not isinstance(instance, StorageBackend):
                raise TypeError(f"{cls_name} does not implement StorageBackend")
            return instance
        except (ModuleNotFoundError, AttributeError, TypeError) as e:
            # Show available backends to help debug
            raise ImportError(
                f"Could not load storage backend '{storage_type}': {e}\n"
                "Valid storage types: file, obsidian, hybrid, (add your own...)"
            )

    def reload_backend(self, config=None):
        if config is not None:
            self._config = config
        self.backend = self._load_backend()

    def __getattr__(self, name):
        return getattr(self.backend, name)


def get_storage_backend(config):
    """
    Returns the actual storage backend instance based on config.
    Use this to get a raw backend if you don't want a router wrapper.
    """
    return StorageRouter(config).backend
