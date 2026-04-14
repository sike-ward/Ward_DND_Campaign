import json
import os
import shutil
from datetime import datetime
from typing import Optional

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


class FileStorage(StorageBackend):
    def __init__(self, root: str):
        self.root = root

    # --- CRUD for all models (JSON storage as example) ---
    def _model_path(self, model, obj_id: str) -> str:
        return os.path.join(self.root, f"{model}_{obj_id}.json")

    def save_user(self, user: User) -> None:
        with open(self._model_path("user", user.id), "w", encoding="utf-8") as f:
            json.dump(user.model_dump(), f, indent=2)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        path = self._model_path("user", user_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return User.model_validate(json.load(f))

    def get_user_by_email(self, email: str) -> Optional[User]:
        for fname in os.listdir(self.root):
            if fname.startswith("user_") and fname.endswith(".json"):
                with open(os.path.join(self.root, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("email") == email:
                        return User.model_validate(data)
        return None

    def delete_user_by_id(self, user_id: str) -> None:
        os.remove(self._model_path("user", user_id))

    def save_group(self, group: Group) -> None:
        with open(self._model_path("group", group.id), "w", encoding="utf-8") as f:
            json.dump(group.model_dump(), f, indent=2)

    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        path = self._model_path("group", group_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Group.model_validate(json.load(f))

    def delete_group_by_id(self, group_id: str) -> None:
        os.remove(self._model_path("group", group_id))

    def save_vault(self, vault: Vault) -> None:
        with open(self._model_path("vault", vault.id), "w", encoding="utf-8") as f:
            json.dump(vault.model_dump(), f, indent=2)

    def get_vault_by_id(self, vault_id: str) -> Optional[Vault]:
        path = self._model_path("vault", vault_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Vault.model_validate(json.load(f))

    def delete_vault_by_id(self, vault_id: str) -> None:
        os.remove(self._model_path("vault", vault_id))

    def save_folder(self, folder: Folder) -> None:
        with open(self._model_path("folder", folder.id), "w", encoding="utf-8") as f:
            json.dump(folder.model_dump(), f, indent=2)

    def get_folder_by_id(self, folder_id: str) -> Optional[Folder]:
        path = self._model_path("folder", folder_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Folder.model_validate(json.load(f))

    def delete_folder_by_id(self, folder_id: str) -> None:
        os.remove(self._model_path("folder", folder_id))

    def save_note(self, note: Note) -> None:
        with open(self._model_path("note", note.id), "w", encoding="utf-8") as f:
            json.dump(note.model_dump(), f, indent=2)

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        path = self._model_path("note", note_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Note.model_validate(json.load(f))

    def delete_note_by_id(self, note_id: str) -> None:
        os.remove(self._model_path("note", note_id))

    def save_character(self, character: Character) -> None:
        with open(self._model_path("character", character.id), "w", encoding="utf-8") as f:
            json.dump(character.model_dump(), f, indent=2)

    def get_character_by_id(self, character_id: str) -> Optional[Character]:
        path = self._model_path("character", character_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Character.model_validate(json.load(f))

    def delete_character_by_id(self, character_id: str) -> None:
        os.remove(self._model_path("character", character_id))

    def save_map(self, map_obj: Map) -> None:
        with open(self._model_path("map", map_obj.id), "w", encoding="utf-8") as f:
            json.dump(map_obj.model_dump(), f, indent=2)

    def get_map_by_id(self, map_id: str) -> Optional[Map]:
        path = self._model_path("map", map_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Map.model_validate(json.load(f))

    def delete_map_by_id(self, map_id: str) -> None:
        os.remove(self._model_path("map", map_id))

    def save_image(self, image: Image) -> None:
        with open(self._model_path("image", image.id), "w", encoding="utf-8") as f:
            json.dump(image.model_dump(), f, indent=2)

    def get_image_by_id(self, image_id: str) -> Optional[Image]:
        path = self._model_path("image", image_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Image.model_validate(json.load(f))

    def delete_image_by_id(self, image_id: str) -> None:
        os.remove(self._model_path("image", image_id))

    def save_sound(self, sound: Sound) -> None:
        with open(self._model_path("sound", sound.id), "w", encoding="utf-8") as f:
            json.dump(sound.model_dump(), f, indent=2)

    def get_sound_by_id(self, sound_id: str) -> Optional[Sound]:
        path = self._model_path("sound", sound_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Sound.model_validate(json.load(f))

    def delete_sound_by_id(self, sound_id: str) -> None:
        os.remove(self._model_path("sound", sound_id))

    def save_session(self, session: Session) -> None:
        with open(self._model_path("session", session.id), "w", encoding="utf-8") as f:
            json.dump(session.model_dump(), f, indent=2)

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        path = self._model_path("session", session_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Session.model_validate(json.load(f))

    def delete_session_by_id(self, session_id: str) -> None:
        os.remove(self._model_path("session", session_id))

    # --- File/folder helpers ---
    def list_folders(self, parent=""):
        path = os.path.join(self.root, parent)
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    def list_notes(self, folder=""):
        path = os.path.join(self.root, folder)
        return [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name)) and name.endswith(".md")]

    def create_folder(self, path):
        os.makedirs(os.path.join(self.root, path), exist_ok=True)

    def delete_folder(self, path):
        shutil.rmtree(os.path.join(self.root, path), ignore_errors=True)

    def move_folder(self, src_path, dest_path):
        shutil.move(os.path.join(self.root, src_path), os.path.join(self.root, dest_path))

    def folder_exists(self, path):
        return os.path.isdir(os.path.join(self.root, path))

    def read_note(self, path):
        with open(os.path.join(self.root, path), "r", encoding="utf-8") as f:
            return f.read()

    def write_note(self, path, content):
        with open(os.path.join(self.root, path), "w", encoding="utf-8") as f:
            f.write(content)

    def delete_note(self, path):
        os.remove(os.path.join(self.root, path))

    def note_exists(self, path):
        return os.path.isfile(os.path.join(self.root, path))

    def move_note(self, src_path, dest_path):
        shutil.move(os.path.join(self.root, src_path), os.path.join(self.root, dest_path))

    def copy_note(self, src_path, dest_path):
        shutil.copy2(os.path.join(self.root, src_path), os.path.join(self.root, dest_path))

    def get_note_metadata(self, path):
        stat = os.stat(os.path.join(self.root, path))
        return {"ctime": stat.st_ctime, "mtime": stat.st_mtime, "size": stat.st_size}

    def get_folder_metadata(self, path):
        stat = os.stat(os.path.join(self.root, path))
        return {"ctime": stat.st_ctime, "mtime": stat.st_mtime}

    # --- Favorites/stars ---
    def read_starred(self):
        star_path = os.path.join(self.root, ".starred.json")
        if not os.path.exists(star_path):
            return set()
        with open(star_path, "r", encoding="utf-8") as f:
            return set(json.load(f))

    def write_starred(self, stars):
        star_path = os.path.join(self.root, ".starred.json")
        with open(star_path, "w", encoding="utf-8") as f:
            json.dump(list(stars), f)

    # --- Versioning/backups ---
    def backup_note(self, note_path):
        orig = os.path.join(self.root, note_path)
        version_dir = os.path.join(self.root, ".versions", os.path.dirname(note_path))
        os.makedirs(version_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        version_name = f"{os.path.basename(note_path)}.{timestamp}.bak"
        backup_path = os.path.join(version_dir, version_name)
        shutil.copy2(orig, backup_path)
        return backup_path

    def list_note_versions(self, note_path):
        version_dir = os.path.join(self.root, ".versions", os.path.dirname(note_path))
        if not os.path.isdir(version_dir):
            return []
        pattern = os.path.splitext(os.path.basename(note_path))[0]
        return [f for f in os.listdir(version_dir) if f.startswith(pattern) and f.endswith(".bak")]

    def restore_note_version(self, note_path, version):
        version_dir = os.path.join(self.root, ".versions", os.path.dirname(note_path))
        version_file = os.path.join(version_dir, version)
        orig = os.path.join(self.root, note_path)
        shutil.copy2(version_file, orig)

    # --- Attachments ---
    def list_attachments(self, folder=""):
        path = os.path.join(self.root, folder)
        return [
            name for name in os.listdir(path) if not name.endswith(".md") and os.path.isfile(os.path.join(path, name))
        ]

    def add_attachment(self, folder, filename, data):
        full_path = os.path.join(self.root, folder, filename)
        with open(full_path, "wb") as f:
            f.write(data)

    def delete_attachment(self, path):
        os.remove(os.path.join(self.root, path))
