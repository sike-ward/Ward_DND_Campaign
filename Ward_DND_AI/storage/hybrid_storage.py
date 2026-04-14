import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Set

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
from Ward_DND_AI.storage.storage_base import StorageBackend


class HybridStorage(StorageBackend):
    """
    Hybrid backend: notes/folders as markdown+folders in vault,
    DND models as JSON in .dnd_meta,
    users/groups in global storage.
    """

    def __init__(self, vault_path, global_data_path="~/.ward_dnd_ai/"):
        self.vault_path = os.path.abspath(vault_path)
        self.global_data_path = os.path.expanduser(global_data_path)
        os.makedirs(self.global_data_path, exist_ok=True)

    # --- Helpers ---
    def _dnd_meta_path(self, subfolder: str, obj_id: str) -> str:
        d = os.path.join(self.vault_path, ".dnd_meta", subfolder)
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, f"{obj_id}.json")

    def _dnd_meta_dir(self, subfolder: str) -> str:
        d = os.path.join(self.vault_path, ".dnd_meta", subfolder)
        os.makedirs(d, exist_ok=True)
        return d

    def _global_path(self, model: str) -> str:
        return os.path.join(self.global_data_path, f"{model}s.json")

    def _load_global(self, model: str) -> Dict:
        path = self._global_path(model)
        if not os.path.isfile(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_global(self, model: str, data: Dict):
        path = self._global_path(model)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # --- USERS ---
    def save_user(self, user: User) -> None:
        users = self._load_global("user")
        users[user.id] = user.model_dump()
        self._save_global("user", users)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        users = self._load_global("user")
        data = users.get(user_id)
        return User.model_validate(data) if data else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        users = self._load_global("user")
        for data in users.values():
            if data.get("email") == email:
                return User.model_validate(data)
        return None

    def delete_user_by_id(self, user_id: str) -> None:
        users = self._load_global("user")
        if user_id in users:
            del users[user_id]
            self._save_global("user", users)

    # --- GROUPS ---
    def save_group(self, group: Group) -> None:
        groups = self._load_global("group")
        groups[group.id] = group.model_dump()
        self._save_global("group", groups)

    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        groups = self._load_global("group")
        data = groups.get(group_id)
        return Group.model_validate(data) if data else None

    def delete_group_by_id(self, group_id: str) -> None:
        groups = self._load_global("group")
        if group_id in groups:
            del groups[group_id]
            self._save_global("group", groups)

    # --- VAULTS ---
    def save_vault(self, vault: Vault) -> None:
        path = self._dnd_meta_path("vaults", vault.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(vault.model_dump(), f, indent=2)

    def get_vault_by_id(self, vault_id: str) -> Optional[Vault]:
        path = self._dnd_meta_path("vaults", vault_id)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Vault.model_validate(json.load(f))

    def delete_vault_by_id(self, vault_id: str) -> None:
        path = self._dnd_meta_path("vaults", vault_id)
        if os.path.isfile(path):
            os.remove(path)

    # --- FOLDERS ---
    def save_folder(self, folder: Folder) -> None:
        if folder.path:
            abs_path = os.path.join(self.vault_path, folder.path)
            os.makedirs(abs_path, exist_ok=True)
        # Save folder metadata
        meta_path = self._dnd_meta_path("folders", folder.id)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(folder.model_dump(), f, indent=2)

    def get_folder_by_id(self, folder_id: str) -> Optional[Folder]:
        abs_path = os.path.join(self.vault_path, folder_id)
        meta_path = self._dnd_meta_path("folders", folder_id)
        if os.path.isdir(abs_path) and os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                return Folder.model_validate(json.load(f))
        elif os.path.isdir(abs_path):
            return Folder(id=folder_id, name=os.path.basename(folder_id), path=folder_id)
        return None

    def delete_folder_by_id(self, folder_id: str) -> None:
        abs_path = os.path.join(self.vault_path, folder_id)
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        meta_path = self._dnd_meta_path("folders", folder_id)
        if os.path.isfile(meta_path):
            os.remove(meta_path)

    def list_folders(self, parent: str = "") -> List[str]:
        root = self.vault_path if not parent else os.path.join(self.vault_path, parent)
        folders = []
        for dirpath, dirnames, _ in os.walk(root):
            for d in dirnames:
                rel_path = os.path.relpath(os.path.join(dirpath, d), self.vault_path)
                folders.append(rel_path)
        return folders

    def create_folder(self, path: str) -> None:
        abs_path = os.path.join(self.vault_path, path)
        os.makedirs(abs_path, exist_ok=True)

    def delete_folder(self, path: str) -> None:
        abs_path = os.path.join(self.vault_path, path)
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)

    def folder_exists(self, path: str) -> bool:
        abs_path = os.path.join(self.vault_path, path)
        return os.path.isdir(abs_path)

    def move_folder(self, src_path: str, dest_path: str) -> None:
        src = os.path.join(self.vault_path, src_path)
        dst = os.path.join(self.vault_path, dest_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)

    def get_folder_metadata(self, path: str) -> Dict:
        abs_path = os.path.join(self.vault_path, path)
        return {
            "path": path,
            "created": datetime.fromtimestamp(os.path.getctime(abs_path)).isoformat(),
            "modified": datetime.fromtimestamp(os.path.getmtime(abs_path)).isoformat(),
        }

    # --- NOTES ---
    def save_note(self, note: Note) -> None:
        if note.path:
            abs_path = os.path.join(self.vault_path, note.path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(note.content)
        meta_path = self._dnd_meta_path("notes", note.id)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(note.model_dump(), f, indent=2)

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        abs_path = os.path.join(self.vault_path, note_id)
        meta_path = self._dnd_meta_path("notes", note_id)
        if not os.path.isfile(abs_path):
            return None
        # Prefer metadata if present
        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                content = self.read_note(note_id)
                data["content"] = content
                return Note.model_validate(data)
        # Otherwise, just basic Note
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Note(id=note_id, name=os.path.basename(note_id), path=note_id, content=content)

    def delete_note_by_id(self, note_id: str) -> None:
        abs_path = os.path.join(self.vault_path, note_id)
        if os.path.isfile(abs_path):
            os.remove(abs_path)
        meta_path = self._dnd_meta_path("notes", note_id)
        if os.path.isfile(meta_path):
            os.remove(meta_path)

    def list_notes(self, folder: str = "") -> List[str]:
        folder_path = self.vault_path if not folder else os.path.join(self.vault_path, folder)
        notes = []
        for dirpath, _, filenames in os.walk(folder_path):
            for fname in filenames:
                if fname.endswith(".md"):
                    rel_path = os.path.relpath(os.path.join(dirpath, fname), self.vault_path)
                    notes.append(rel_path)
        return notes

    def read_note(self, path: str) -> str:
        abs_path = os.path.join(self.vault_path, path)
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()

    def write_note(self, path: str, content: str) -> None:
        abs_path = os.path.join(self.vault_path, path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

    def delete_note(self, path: str) -> None:
        abs_path = os.path.join(self.vault_path, path)
        if os.path.isfile(abs_path):
            os.remove(abs_path)

    def note_exists(self, path: str) -> bool:
        abs_path = os.path.join(self.vault_path, path)
        return os.path.isfile(abs_path)

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

    def get_note_metadata(self, path: str) -> Dict:
        abs_path = os.path.join(self.vault_path, path)
        return {
            "path": path,
            "created": datetime.fromtimestamp(os.path.getctime(abs_path)).isoformat(),
            "modified": datetime.fromtimestamp(os.path.getmtime(abs_path)).isoformat(),
        }

    # --- CHARACTERS ---
    def save_character(self, character: Character) -> None:
        path = self._dnd_meta_path("characters", character.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(character.model_dump(), f, indent=2)

    def get_character_by_id(self, character_id: str) -> Optional[Character]:
        path = self._dnd_meta_path("characters", character_id)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Character.model_validate(json.load(f))

    def delete_character_by_id(self, character_id: str) -> None:
        path = self._dnd_meta_path("characters", character_id)
        if os.path.isfile(path):
            os.remove(path)

    # --- MAPS ---
    def save_map(self, map_obj: Map) -> None:
        path = self._dnd_meta_path("maps", map_obj.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(map_obj.model_dump(), f, indent=2)

    def get_map_by_id(self, map_id: str) -> Optional[Map]:
        path = self._dnd_meta_path("maps", map_id)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Map.model_validate(json.load(f))

    def delete_map_by_id(self, map_id: str) -> None:
        path = self._dnd_meta_path("maps", map_id)
        if os.path.isfile(path):
            os.remove(path)

    # --- IMAGES ---
    def save_image(self, image: Image) -> None:
        path = self._dnd_meta_path("images", image.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(image.model_dump(), f, indent=2)

    def get_image_by_id(self, image_id: str) -> Optional[Image]:
        path = self._dnd_meta_path("images", image_id)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Image.model_validate(json.load(f))

    def delete_image_by_id(self, image_id: str) -> None:
        path = self._dnd_meta_path("images", image_id)
        if os.path.isfile(path):
            os.remove(path)

    # --- SOUNDS ---
    def save_sound(self, sound: Sound) -> None:
        path = self._dnd_meta_path("sounds", sound.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sound.model_dump(), f, indent=2)

    def get_sound_by_id(self, sound_id: str) -> Optional[Sound]:
        path = self._dnd_meta_path("sounds", sound_id)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Sound.model_validate(json.load(f))

    def delete_sound_by_id(self, sound_id: str) -> None:
        path = self._dnd_meta_path("sounds", sound_id)
        if os.path.isfile(path):
            os.remove(path)

    # --- SESSIONS ---
    def save_session(self, session: Session) -> None:
        path = self._dnd_meta_path("sessions", session.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session.model_dump(), f, indent=2)

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        path = self._dnd_meta_path("sessions", session_id)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Session.model_validate(json.load(f))

    def delete_session_by_id(self, session_id: str) -> None:
        path = self._dnd_meta_path("sessions", session_id)
        if os.path.isfile(path):
            os.remove(path)

    # --- TIMELINE ---
    def read_timeline(self) -> list:
        path = os.path.join(self.vault_path, ".dnd_meta", "timeline.json")
        if not os.path.isfile(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def save_timeline(self, events: list) -> None:
        meta_dir = os.path.join(self.vault_path, ".dnd_meta")
        os.makedirs(meta_dir, exist_ok=True)
        path = os.path.join(meta_dir, "timeline.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)

    # --- STARS/FAVORITES ---
    def read_starred(self) -> Set[str]:
        star_path = os.path.join(self.vault_path, ".starred.json")
        if not os.path.exists(star_path):
            return set()
        with open(star_path, "r", encoding="utf-8") as f:
            return set(json.load(f))

    def write_starred(self, stars: Set[str]) -> None:
        star_path = os.path.join(self.vault_path, ".starred.json")
        with open(star_path, "w", encoding="utf-8") as f:
            json.dump(list(stars), f)

    # --- VERSIONING/BACKUPS ---
    def backup_note(self, note_path: str) -> str:
        orig = os.path.join(self.vault_path, note_path)
        version_dir = os.path.join(self.vault_path, ".versions", os.path.dirname(note_path))
        os.makedirs(version_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        version_name = f"{os.path.basename(note_path)}.{timestamp}.bak"
        backup_path = os.path.join(version_dir, version_name)
        shutil.copy2(orig, backup_path)
        return backup_path

    def list_note_versions(self, note_path: str) -> List[str]:
        version_dir = os.path.join(self.vault_path, ".versions", os.path.dirname(note_path))
        if not os.path.isdir(version_dir):
            return []
        pattern = os.path.splitext(os.path.basename(note_path))[0]
        return [f for f in os.listdir(version_dir) if f.startswith(pattern) and f.endswith(".bak")]

    def restore_note_version(self, note_path: str, version: str) -> None:
        version_dir = os.path.join(self.vault_path, ".versions", os.path.dirname(note_path))
        version_file = os.path.join(version_dir, version)
        orig = os.path.join(self.vault_path, note_path)
        shutil.copy2(version_file, orig)

    # --- ATTACHMENTS ---
    def list_attachments(self, folder: str = "") -> List[str]:
        path = os.path.join(self.vault_path, "_attachments", folder)
        if not os.path.isdir(path):
            return []
        return [
            name for name in os.listdir(path) if not name.endswith(".md") and os.path.isfile(os.path.join(path, name))
        ]

    def add_attachment(self, folder: str, filename: str, data: bytes) -> None:
        dest = os.path.join(self.vault_path, "_attachments", folder, filename)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)

    def delete_attachment(self, path: str) -> None:
        abs_path = os.path.join(self.vault_path, "_attachments", path)
        if os.path.isfile(abs_path):
            os.remove(abs_path)
