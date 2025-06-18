## Ward_DND_AI/storage/storage_router.py

import importlib

from Ward_DND_AI.storage.storage_base import StorageBackend


class StorageRouter:
    def __init__(self, config):
        self._config = config
        self.backend = self._load_backend()

    def _load_backend(self) -> StorageBackend:
        storage_type = self._config.VAULT_TYPE.lower()
        module_name = f"Ward_DND_AI.storage.{storage_type}_storage"
        cls_name = f"{storage_type.capitalize()}Storage"
        try:
            module = importlib.import_module(module_name)
            backend_cls = getattr(module, cls_name)
            instance = backend_cls(self._config.VAULT_PATH)
            if not isinstance(instance, StorageBackend):
                raise TypeError(f"{cls_name} does not implement StorageBackend")
            return instance
        except (ModuleNotFoundError, AttributeError, TypeError) as e:
            raise ImportError(f"Could not load storage backend '{storage_type}': {e}")

    def __getattr__(self, name):
        return getattr(self.backend, name)


def get_storage_backend(config):
    return StorageRouter(config).backend
