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
