import os
from datetime import datetime

from Ward_DND_AI.storage.storage_base import BaseStorageBackend


class ObsidianStorage(BaseStorageBackend):
    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    def list_all_notes(self, folder: str = ""):
        notes = []
        target = os.path.join(self.vault_path, folder)
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith(".md"):
                    rel_path = os.path.relpath(
                        os.path.join(root, file), self.vault_path
                    )
                    notes.append(rel_path.replace("\\", "/"))
        return notes

    def list_tags(self):
        # Placeholder for future implementation
        return []

    def read_note(self, rel_path: str):
        abs_path = os.path.join(self.vault_path, rel_path)
        if not os.path.exists(abs_path):
            return ("", "")
        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        title = lines[0].strip("# \n") if lines else "Untitled"
        body = "".join(lines[1:]) if len(lines) > 1 else ""
        return title, body

    def save_note(
        self, folder: str, filename: str, heading: str, prompt: str, linked_body: str
    ):
        folder_path = os.path.join(self.vault_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        filepath = os.path.join(folder_path, f"{filename}.md")
        content = (
            f"# {heading}\n"
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
            f"**Prompt:** {prompt}\n\n"
            f"{linked_body}"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.relpath(filepath, self.vault_path).replace("\\", "/")

    def get_all_folders(self):
        folders = set()
        for root, _, files in os.walk(self.vault_path):
            if any(f.endswith(".md") for f in files):
                rel = os.path.relpath(root, self.vault_path)
                folders.add("" if rel == "." else rel.replace("\\", "/"))
        return sorted(folders)

    def list_folders(self) -> list[str]:
        return self.get_all_folders()

    def delete_note(self, rel_path: str):
        abs_path = os.path.join(self.vault_path, rel_path)
        if os.path.exists(abs_path):
            os.remove(abs_path)
            return True
        return False
