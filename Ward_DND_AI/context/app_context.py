from Ward_DND_AI.config.config import Config
from Ward_DND_AI.storage.hybrid_storage import HybridStorage


class AppContext:
    """
    Application context / service locator for storage backends.
    Holds configuration and instantiates storage engines via dependency injection.
    """

    def __init__(self, config: Config):
        self.config = config

        # Hybrid storage for both core and vault data
        # You can separate paths if you want, or just use VAULT_PATH for both
        self.core_storage = HybridStorage(config.CORE_DATA_PATH)
        self.storage = HybridStorage(config.VAULT_PATH)
