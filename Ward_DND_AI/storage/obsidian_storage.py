## Ward_DND_AI/storage/obsidian_storage.py
import os
from typing import List

from Ward_DND_AI.storage.storage_base import StorageBackend


class ObsidianStorage(StorageBackend):
    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    def list_folders(self) -> List[str]:
        folders = []
        for dirpath, _, _ in os.walk(self.vault_path):
            rel = os.path.relpath(dirpath, self.vault_path)
            if rel != ".":
                folders.append(rel)
        return folders

    def list_notes(self, folder: str) -> List[str]:
        base = os.path.join(self.vault_path, folder) if folder else self.vault_path
        if not os.path.isdir(base):
            return []
        return [
            f
            for f in os.listdir(base)
            if f.endswith(".md") and os.path.isfile(os.path.join(base, f))
        ]

    def list_all_notes(self) -> List[str]:
        notes = []
        for folder in self.list_folders() + [""]:
            prefix = f"{folder}{os.sep}" if folder else ""
            notes.extend(prefix + n for n in self.list_notes(folder))
        return notes

    def read_note(self, path: str) -> str:
        full = os.path.join(self.vault_path, path)
        with open(full, "r", encoding="utf-8") as f:
            return f.read()

    def write_note(self, path: str, content: str) -> None:
        # ensure .md extension
        rel = path if path.endswith(".md") else f"{path}.md"
        full = os.path.join(self.vault_path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    def delete_note(self, path: str) -> None:
        full = os.path.join(self.vault_path, path)
        if os.path.exists(full):
            os.remove(full)

    def list_tags(self) -> List[str]:
        tags = set()
        for note in self.list_all_notes():
            for word in self.read_note(note).split():
                if word.startswith("#"):
                    tags.add(word.lstrip("#"))
        return list(tags)

    def search_notes(self, query: str, top_k: int = 10) -> List[str]:
        matches = []
        for note in self.list_all_notes():
            if query.lower() in self.read_note(note).lower():
                matches.append(note)
                if len(matches) >= top_k:
                    break
        return matches
