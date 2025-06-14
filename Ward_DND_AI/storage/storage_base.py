from abc import ABC, abstractmethod


class BaseStorageBackend(ABC):
    @abstractmethod
    def list_all_notes(self, folder: str) -> list[str]:
        pass

    @abstractmethod
    def read_note(self, note_path: str) -> tuple[str, str]:
        pass

    @abstractmethod
    def list_tags(self) -> list[str]:
        pass

    @abstractmethod
    def list_folders(self) -> list[str]:
        pass
