import os
from typing import Tuple

from Ward_DND_AI.storage import BaseStorageBackend


class FileStorageBackend(BaseStorageBackend):
    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    def list_all_notes(self, folder: str) -> list[str]:
        path = os.path.join(self.vault_path, folder)
        if not os.path.exists(path):
            return []
        return [
            os.path.join(folder, f)
            for f in os.listdir(path)
            if f.endswith(".md") and os.path.isfile(os.path.join(path, f))
        ]

    def read_note(self, note_path: str) -> Tuple[str, str]:
        full_path = os.path.join(self.vault_path, note_path)
        if not os.path.exists(full_path):
            return "", ""
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].strip().lstrip("#") if lines else "Untitled"
            body = "".join(lines[1:]) if len(lines) > 1 else ""
        return title, body

    def list_tags(self) -> list[str]:
        # Placeholder: implement tag parsing logic later
        return []

    def list_folders(self) -> list[str]:
        folders = []
        for root, dirs, _ in os.walk(self.vault_path):
            for d in dirs:
                folders.append(os.path.relpath(os.path.join(root, d), self.vault_path))
        return folders
