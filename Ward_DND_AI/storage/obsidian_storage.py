## Ward_DND_AI/storage/obsidian_storage.py
import os
import shutil
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

    # --- Note Operations ---

    def exists(self, path: str) -> bool:
        full = os.path.join(self.vault_path, path)
        return os.path.exists(full)

    def move_note(self, src_path: str, dest_path: str) -> None:
        src = os.path.join(self.vault_path, src_path)
        dst = os.path.join(self.vault_path, dest_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)

    def copy_note(self, src_path: str, dest_path: str) -> None:
        src = os.path.join(self.vault_path, src_path)
        dst = os.path.join(self.vault_path, dest_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    # --- Folder Operations ---

    def create_folder(self, path: str) -> None:
        full = os.path.join(self.vault_path, path)
        os.makedirs(full, exist_ok=True)

    def delete_folder(self, path: str) -> None:
        full = os.path.join(self.vault_path, path)
        if os.path.isdir(full):
            shutil.rmtree(full)

    def move_folder(self, src_path: str, dest_path: str) -> None:
        src = os.path.join(self.vault_path, src_path)
        dst = os.path.join(self.vault_path, dest_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)

    def folder_exists(self, path: str) -> bool:
        full = os.path.join(self.vault_path, path)
        return os.path.isdir(full)

    # --- Metadata and Utility ---

    def get_note_metadata(self, path: str) -> dict:
        full = os.path.join(self.vault_path, path)
        if not os.path.isfile(full):
            return {}
        stat = os.stat(full)
        return {
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "path": path,
            "name": os.path.basename(path),
        }

    def get_folder_metadata(self, path: str) -> dict:
        full = os.path.join(self.vault_path, path)
        if not os.path.isdir(full):
            return {}
        stat = os.stat(full)
        note_count = len(self.list_notes(path))
        return {
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "path": path,
            "name": os.path.basename(path),
            "note_count": note_count,
        }

    # --- Advanced/Optional Features for future-proofing ---

    def rename_note(self, old_path: str, new_path: str) -> None:
        return self.move_note(old_path, new_path)

    def list_attachments(self, folder: str = "") -> list:
        folder_path = (
            os.path.join(self.vault_path, folder) if folder else self.vault_path
        )
        if not os.path.isdir(folder_path):
            return []
        # Attachments = not ending with .md and not a directory
        return [
            f
            for f in os.listdir(folder_path)
            if not f.endswith(".md") and os.path.isfile(os.path.join(folder_path, f))
        ]

    def add_attachment(self, folder: str, filename: str, data: bytes) -> None:
        folder_path = os.path.join(self.vault_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        with open(os.path.join(folder_path, filename), "wb") as f:
            f.write(data)

    def delete_attachment(self, path: str) -> None:
        full = os.path.join(self.vault_path, path)
        if os.path.exists(full):
            os.remove(full)

    def sync(self) -> None:
        # For local storage, do nothing (cloud/network can override)
        pass

    def get_change_log(self, since_timestamp: float = 0) -> list:
        # Not implemented for local files; override for multiplayer/network
        return []

    def lock_note(self, path: str, user_id: str) -> bool:
        # Not implemented for local; always returns True (override for multiplayer)
        return True

    def unlock_note(self, path: str, user_id: str) -> None:
        # Not implemented for local; no-op
        pass
