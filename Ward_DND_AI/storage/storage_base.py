from abc import ABC, abstractmethod
from typing import List, Optional, Set

from Ward_DND_AI.models.character import Character
from Ward_DND_AI.models.folder import Folder
from Ward_DND_AI.models.group import Group
from Ward_DND_AI.models.image import Image
from Ward_DND_AI.models.map import Map
from Ward_DND_AI.models.note import Note
from Ward_DND_AI.models.session import Session
from Ward_DND_AI.models.sound import Sound
from Ward_DND_AI.models.user import User
from Ward_DND_AI.models.vault import Vault


class StorageBackend(ABC):
    # --- CRUD for ALL MODELS ---
    @abstractmethod
    def save_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def delete_user_by_id(self, user_id: str) -> None:
        pass

    @abstractmethod
    def save_group(self, group: Group) -> None:
        pass

    @abstractmethod
    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        pass

    @abstractmethod
    def delete_group_by_id(self, group_id: str) -> None:
        pass

    @abstractmethod
    def save_vault(self, vault: Vault) -> None:
        pass

    @abstractmethod
    def get_vault_by_id(self, vault_id: str) -> Optional[Vault]:
        pass

    @abstractmethod
    def delete_vault_by_id(self, vault_id: str) -> None:
        pass

    @abstractmethod
    def save_folder(self, folder: Folder) -> None:
        pass

    @abstractmethod
    def get_folder_by_id(self, folder_id: str) -> Optional[Folder]:
        pass

    @abstractmethod
    def delete_folder_by_id(self, folder_id: str) -> None:
        pass

    @abstractmethod
    def save_note(self, note: Note) -> None:
        pass

    @abstractmethod
    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        pass

    @abstractmethod
    def delete_note_by_id(self, note_id: str) -> None:
        pass

    @abstractmethod
    def save_character(self, character: Character) -> None:
        pass

    @abstractmethod
    def get_character_by_id(self, character_id: str) -> Optional[Character]:
        pass

    @abstractmethod
    def delete_character_by_id(self, character_id: str) -> None:
        pass

    @abstractmethod
    def save_map(self, map_obj: Map) -> None:
        pass

    @abstractmethod
    def get_map_by_id(self, map_id: str) -> Optional[Map]:
        pass

    @abstractmethod
    def delete_map_by_id(self, map_id: str) -> None:
        pass

    @abstractmethod
    def save_image(self, image: Image) -> None:
        pass

    @abstractmethod
    def get_image_by_id(self, image_id: str) -> Optional[Image]:
        pass

    @abstractmethod
    def delete_image_by_id(self, image_id: str) -> None:
        pass

    @abstractmethod
    def save_sound(self, sound: Sound) -> None:
        pass

    @abstractmethod
    def get_sound_by_id(self, sound_id: str) -> Optional[Sound]:
        pass

    @abstractmethod
    def delete_sound_by_id(self, sound_id: str) -> None:
        pass

    @abstractmethod
    def save_session(self, session: Session) -> None:
        pass

    @abstractmethod
    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        pass

    @abstractmethod
    def delete_session_by_id(self, session_id: str) -> None:
        pass

    # --- GENERIC FILE & FOLDER HELPERS ---
    @abstractmethod
    def list_folders(self, parent: str = "") -> List[str]:
        pass

    @abstractmethod
    def list_notes(self, folder: str = "") -> List[str]:
        pass

    @abstractmethod
    def create_folder(self, path: str) -> None:
        pass

    @abstractmethod
    def delete_folder(self, path: str) -> None:
        pass

    @abstractmethod
    def move_folder(self, src_path: str, dest_path: str) -> None:
        pass

    @abstractmethod
    def folder_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def read_note(self, path: str) -> str:
        pass

    @abstractmethod
    def write_note(self, path: str, content: str) -> None:
        pass

    @abstractmethod
    def delete_note(self, path: str) -> None:
        pass

    @abstractmethod
    def note_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def move_note(self, src_path: str, dest_path: str) -> None:
        pass

    @abstractmethod
    def copy_note(self, src_path: str, dest_path: str) -> None:
        pass

    @abstractmethod
    def get_note_metadata(self, path: str) -> dict:
        pass

    @abstractmethod
    def get_folder_metadata(self, path: str) -> dict:
        pass

    # --- FAVORITES/STARS ---
    @abstractmethod
    def read_starred(self) -> Set[str]:
        pass

    @abstractmethod
    def write_starred(self, stars: Set[str]) -> None:
        pass

    # --- VERSIONING/BACKUPS ---
    @abstractmethod
    def backup_note(self, note_path: str) -> str:
        pass

    @abstractmethod
    def list_note_versions(self, note_path: str) -> List[str]:
        pass

    @abstractmethod
    def restore_note_version(self, note_path: str, version: str) -> None:
        pass

    # --- ATTACHMENTS ---
    @abstractmethod
    def list_attachments(self, folder: str = "") -> List[str]:
        pass

    @abstractmethod
    def add_attachment(self, folder: str, filename: str, data: bytes) -> None:
        pass

    @abstractmethod
    def delete_attachment(self, path: str) -> None:
        pass
