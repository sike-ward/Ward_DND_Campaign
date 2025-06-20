# Ward_DND_AI/storage/storage_base.py

from abc import ABC, abstractmethod
from typing import List


class StorageBackend(ABC):
    """
    Abstract base class for all storage backends.
    Every backend must implement these methods so that controllers
    can interact with notes in a uniform way.
    """

    @abstractmethod
    def list_folders(self) -> List[str]:
        """
        Return a list of all folder names in the vault.
        """
        pass

    @abstractmethod
    def list_notes(self, folder: str) -> List[str]:
        """
        Return a list of note filenames (without path) in the given folder.
        """
        pass

    @abstractmethod
    def list_all_notes(self) -> List[str]:
        """
        Return a list of all note paths (relative) across all folders.
        """
        pass

    @abstractmethod
    def read_note(self, path: str) -> str:
        """
        Return the full raw content of the note at the given relative path.
        """
        pass

    @abstractmethod
    def write_note(self, path: str, content: str) -> None:
        """
        Create or overwrite the note at the given relative path with the provided content.
        """
        pass

    @abstractmethod
    def delete_note(self, path: str) -> None:
        """
        Delete the note at the given relative path.
        """
        pass

    @abstractmethod
    def list_tags(self) -> List[str]:
        """
        Return a deduplicated list of all tags found across notes.
        """
        pass

    @abstractmethod
    def search_notes(self, query: str, top_k: int = 10) -> List[str]:
        """
        Search across notes for the given query string (or embedding).
        Return up to `top_k` matching note paths.
        """
        pass
        # --- Note Operations ---

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Return True if the note exists at the given relative path.
        """
        pass

    @abstractmethod
    def move_note(self, src_path: str, dest_path: str) -> None:
        """
        Move a note from src_path to dest_path (overwriting if exists).
        """
        pass

    @abstractmethod
    def copy_note(self, src_path: str, dest_path: str) -> None:
        """
        Duplicate a note from src_path to dest_path (overwriting if exists).
        """
        pass

    # --- Folder Operations ---
    @abstractmethod
    def create_folder(self, path: str) -> None:
        """
        Create a new folder at the given relative path.
        """
        pass

    @abstractmethod
    def delete_folder(self, path: str) -> None:
        """
        Delete the folder at the given relative path, including all subfolders and notes.
        """
        pass

    @abstractmethod
    def move_folder(self, src_path: str, dest_path: str) -> None:
        """
        Move/rename a folder (and its contents) from src_path to dest_path.
        """
        pass

    @abstractmethod
    def folder_exists(self, path: str) -> bool:
        """
        Return True if the folder exists at the given relative path.
        """
        pass

    # --- Metadata and Utility ---
    @abstractmethod
    def get_note_metadata(self, path: str) -> dict:
        """
        Return metadata for a note (size, timestamps, tags, etc.) as a dict.
        """
        pass

    @abstractmethod
    def get_folder_metadata(self, path: str) -> dict:
        """
        Return metadata for a folder (creation time, note count, total size, etc.) as a dict.
        """
        pass

    # --- Advanced/Optional Features for future-proofing ---
    @abstractmethod
    def rename_note(self, old_path: str, new_path: str) -> None:
        """
        Rename a note (same as move_note, but clearer for UI logic).
        """
        pass

    @abstractmethod
    def list_attachments(self, folder: str = "") -> list:
        """
        Return a list of non-note files (e.g., images, PDFs, media) in the given folder or whole vault.
        """
        pass

    @abstractmethod
    def add_attachment(self, folder: str, filename: str, data: bytes) -> None:
        """
        Save a binary attachment (e.g., image, file) to the given folder.
        """
        pass

    @abstractmethod
    def delete_attachment(self, path: str) -> None:
        """
        Delete an attachment file at the given relative path.
        """
        pass

    # --- For Multiplayer/Cloud Support ---
    @abstractmethod
    def sync(self) -> None:
        """
        (Optional) Sync storage with remote/cloud if backend supports it.
        """
        pass

    @abstractmethod
    def get_change_log(self, since_timestamp: float = 0) -> list:
        """
        (Optional) Return a list of changes (add, edit, delete) since a given timestamp.
        Used for collaborative/multiplayer sync.
        """
        pass

    @abstractmethod
    def lock_note(self, path: str, user_id: str) -> bool:
        """
        (Optional) Lock a note for editing by a given user; return True if lock is acquired.
        """
        pass

    @abstractmethod
    def unlock_note(self, path: str, user_id: str) -> None:
        """
        (Optional) Release the lock for a note by a given user.
        """
        pass
