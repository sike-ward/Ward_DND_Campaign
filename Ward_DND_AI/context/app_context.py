"""
AppContext — the single service locator for the entire Ward DND AI application.

Every controller and view should receive an AppContext instance rather than
importing managers or storage directly. This keeps dependencies explicit,
makes testing easy (swap out storage/managers via constructor), and gives
a clear picture of what services exist at runtime.

Multiuser design:
- All managers share the same StorageBackend instance so writes are consistent.
- The AI engine is set after construction (main.py wires it up) so startup
  order remains flexible.
- A 'current_user_id' slot is provided for single-user mode; the full auth
  flow will replace this with proper session-based identity later.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from Ward_DND_AI.config.config import Config
from Ward_DND_AI.managers.character_manager import CharacterManager
from Ward_DND_AI.managers.folder_manager import FolderManager
from Ward_DND_AI.managers.group_manager import GroupManager
from Ward_DND_AI.managers.image_manager import ImageManager
from Ward_DND_AI.managers.map_manager import MapManager
from Ward_DND_AI.managers.note_manager import NoteManager
from Ward_DND_AI.managers.session_manager import SessionManager
from Ward_DND_AI.managers.sound_manager import SoundManager
from Ward_DND_AI.managers.user_manager import UserManager
from Ward_DND_AI.managers.vault_manager import VaultManager
from Ward_DND_AI.storage.hybrid_storage import HybridStorage
from Ward_DND_AI.storage.storage_base import StorageBackend

if TYPE_CHECKING:
    from Ward_DND_AI.ai.core.ai_base import AIInterface


class AppContext:
    """
    Central service locator — holds every service the app needs.

    Usage
    -----
    Construct once in main.py and pass to every controller/view:

        ctx = AppContext(config)
        ctx.ai = get_model_backend(config, storage=ctx.storage)

    Then inject into GUI:

        window = LoreMainApp(ctx=ctx)

    Attributes
    ----------
    config : Config
        Loaded application configuration.
    storage : StorageBackend
        Primary storage backend. All managers share this instance.
    ai : AIInterface | None
        AI engine — set by main.py after AppContext is constructed.
    current_user_id : str | None
        Active user for single-user mode. Replace with session-based
        identity when full auth is implemented.
    users : UserManager
    notes : NoteManager
    vaults : VaultManager
    groups : GroupManager
    folders : FolderManager
    characters : CharacterManager
    maps : MapManager
    images : ImageManager
    sounds : SoundManager
    sessions : SessionManager
    """

    def __init__(self, config: Config, storage: Optional[StorageBackend] = None):
        self.config = config

        # Storage — accept an injected backend or build the default HybridStorage.
        # Passing a custom backend makes unit-testing trivial.
        self.storage: StorageBackend = storage or HybridStorage(config.VAULT_PATH)

        # AI engine — wired up by main.py after construction.
        self.ai: Optional[AIInterface] = None

        # Active user slot — placeholder until session-based auth is live.
        self.current_user_id: Optional[str] = None

        # --- Managers — all share the same storage instance ---
        self.users = UserManager(self.storage)
        self.notes = NoteManager(self.storage)
        self.vaults = VaultManager(self.storage)
        self.groups = GroupManager(self.storage)
        self.folders = FolderManager(self.storage)
        self.characters = CharacterManager(self.storage)
        self.maps = MapManager(self.storage)
        self.images = ImageManager(self.storage)
        self.sounds = SoundManager(self.storage)
        self.sessions = SessionManager(self.storage)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def has_ai(self) -> bool:
        """Return True if an AI engine has been wired up."""
        return self.ai is not None

    def require_ai(self) -> "AIInterface":
        """Return the AI engine or raise if not yet wired up."""
        if self.ai is None:
            raise RuntimeError("AI engine has not been initialised on AppContext.")
        return self.ai
