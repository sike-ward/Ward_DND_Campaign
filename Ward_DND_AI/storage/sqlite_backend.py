"""
SQLite Storage Backend for Ward DND AI.

A fully normalized SQLite implementation using SQLAlchemy 2.0 with declarative
ORM. All Pydantic models are stored as JSON blobs to avoid schema coupling.

The backend operates in "hybrid" mode:
  - Structured model data (User, Character, Note metadata) is stored in SQLite.
  - Note content is stored as markdown files in vault_path (delegated to pathlib).
  - Attachments, versions, and search indices are also file-based.

This approach provides ACID semantics for models while maintaining filesystem
flexibility for content. It scales better than pure file-storage but doesn't
require per-model schema migrations.

Thread-safe for multi-threaded PyQt6 applications via create_engine with
check_same_thread=False.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

from sqlalchemy import String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column
from sqlalchemy.types import Mapped

from Ward_DND_AI.models.character import Character
from Ward_DND_AI.models.folder import Folder
from Ward_DND_AI.models.group import Group
from Ward_DND_AI.models.image import Image
from Ward_DND_AI.models.map import Map
from Ward_DND_AI.models.note import Note
from Ward_DND_AI.models.session import Session as SessionModel
from Ward_DND_AI.models.sound import Sound
from Ward_DND_AI.models.user import User
from Ward_DND_AI.models.vault import Vault
from Ward_DND_AI.storage.storage_base import StorageBackend

# ============================================================================
# SQLAlchemy ORM Models
# ============================================================================


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""

    pass


class UserRecord(Base):
    """ORM model for User data — stored as JSON blob."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class GroupRecord(Base):
    """ORM model for Group data — stored as JSON blob."""

    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class VaultRecord(Base):
    """ORM model for Vault data — stored as JSON blob."""

    __tablename__ = "vaults"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class FolderRecord(Base):
    """ORM model for Folder data — stored as JSON blob."""

    __tablename__ = "folders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class NoteRecord(Base):
    """ORM model for Note metadata — content stored as file."""

    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob (metadata only)


class CharacterRecord(Base):
    """ORM model for Character data — stored as JSON blob."""

    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class MapRecord(Base):
    """ORM model for Map data — stored as JSON blob."""

    __tablename__ = "maps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class ImageRecord(Base):
    """ORM model for Image data — stored as JSON blob."""

    __tablename__ = "images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class SoundRecord(Base):
    """ORM model for Sound data — stored as JSON blob."""

    __tablename__ = "sounds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class SessionRecord(Base):
    """ORM model for Session data — stored as JSON blob."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class StarredRecord(Base):
    """Store starred/favorite note IDs (one JSON blob with the entire set)."""

    __tablename__ = "starred"

    id: Mapped[str] = mapped_column(String(1), primary_key=True, default="1")
    data: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON array


# ============================================================================
# SQLiteBackend
# ============================================================================


class SQLiteBackend(StorageBackend):
    """
    SQLAlchemy-based SQLite backend for Ward DND AI.

    All Pydantic models are serialized to JSON and stored as TEXT columns,
    avoiding schema coupling and making future migrations trivial.

    File-system operations (note content, attachments, versions) are delegated
    to pathlib in vault_path, following the same pattern as HybridStorage.

    Parameters
    ----------
    db_path : str
        Path to SQLite database file (e.g., "ward_dnd.db").
        Created automatically if it doesn't exist.
    vault_path : str, optional
        Root directory for markdown notes, attachments, and versions.
        If not provided, defaults to a `.vault` subdirectory next to the DB.
    """

    def __init__(self, db_path: str, vault_path: Optional[str] = None):
        """Initialize SQLite backend and create tables if needed."""
        self.db_path = Path(db_path)
        self.vault_path: Path = Path(vault_path or self.db_path.parent / ".vault").resolve()
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Create engine with check_same_thread=False for PyQt6 thread safety
        db_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})

        # Create all tables on first run
        Base.metadata.create_all(self.engine)

    def _session(self) -> Session:
        """Get a new database session."""
        return Session(self.engine)

    def _dnd_meta_path(self, subfolder: str, obj_id: str) -> Path:
        """Return the JSON path for a model object's metadata, creating dir if needed."""
        d = self.vault_path / ".dnd_meta" / subfolder
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{obj_id}.json"

    def _abs(self, rel: str) -> Path:
        """Resolve a relative vault path to an absolute Path."""
        return self.vault_path / rel

    # ========================================================================
    # Users
    # ========================================================================

    def save_user(self, user: User) -> None:
        """Save or update a User record."""
        with self._session() as session:
            record = session.query(UserRecord).filter(UserRecord.id == user.id).first()
            if record:
                record.data = user.model_dump_json()
            else:
                record = UserRecord(id=user.id, data=user.model_dump_json())
                session.add(record)
            session.commit()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a User by ID."""
        with self._session() as session:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if record:
                return User.model_validate_json(record.data)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a User by email address."""
        with self._session() as session:
            records = session.query(UserRecord).all()
            for record in records:
                user = User.model_validate_json(record.data)
                if user.email == email:
                    return user
        return None

    def delete_user_by_id(self, user_id: str) -> None:
        """Delete a User by ID."""
        with self._session() as session:
            session.query(UserRecord).filter(UserRecord.id == user_id).delete()
            session.commit()

    # ========================================================================
    # Groups
    # ========================================================================

    def save_group(self, group: Group) -> None:
        """Save or update a Group record."""
        with self._session() as session:
            record = session.query(GroupRecord).filter(GroupRecord.id == group.id).first()
            if record:
                record.data = group.model_dump_json()
            else:
                record = GroupRecord(id=group.id, data=group.model_dump_json())
                session.add(record)
            session.commit()

    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        """Retrieve a Group by ID."""
        with self._session() as session:
            record = session.query(GroupRecord).filter(GroupRecord.id == group_id).first()
            if record:
                return Group.model_validate_json(record.data)
        return None

    def delete_group_by_id(self, group_id: str) -> None:
        """Delete a Group by ID."""
        with self._session() as session:
            session.query(GroupRecord).filter(GroupRecord.id == group_id).delete()
            session.commit()

    # ========================================================================
    # Vaults
    # ========================================================================

    def save_vault(self, vault: Vault) -> None:
        """Save or update a Vault record."""
        with self._session() as session:
            record = session.query(VaultRecord).filter(VaultRecord.id == vault.id).first()
            if record:
                record.data = vault.model_dump_json()
            else:
                record = VaultRecord(id=vault.id, data=vault.model_dump_json())
                session.add(record)
            session.commit()

    def get_vault_by_id(self, vault_id: str) -> Optional[Vault]:
        """Retrieve a Vault by ID."""
        with self._session() as session:
            record = session.query(VaultRecord).filter(VaultRecord.id == vault_id).first()
            if record:
                return Vault.model_validate_json(record.data)
        return None

    def delete_vault_by_id(self, vault_id: str) -> None:
        """Delete a Vault by ID."""
        with self._session() as session:
            session.query(VaultRecord).filter(VaultRecord.id == vault_id).delete()
            session.commit()

    # ========================================================================
    # Folders
    # ========================================================================

    def save_folder(self, folder: Folder) -> None:
        """Save or update a Folder record and create its directory."""
        if folder.path:
            self._abs(folder.path).mkdir(parents=True, exist_ok=True)

        with self._session() as session:
            record = session.query(FolderRecord).filter(FolderRecord.id == folder.id).first()
            if record:
                record.data = folder.model_dump_json()
            else:
                record = FolderRecord(id=folder.id, data=folder.model_dump_json())
                session.add(record)
            session.commit()

    def get_folder_by_id(self, folder_id: str) -> Optional[Folder]:
        """Retrieve a Folder by ID."""
        with self._session() as session:
            record = session.query(FolderRecord).filter(FolderRecord.id == folder_id).first()
            if record:
                return Folder.model_validate_json(record.data)
        return None

    def delete_folder_by_id(self, folder_id: str) -> None:
        """Delete a Folder by ID and remove its directory."""
        abs_path = self._abs(folder_id)
        if abs_path.is_dir():
            shutil.rmtree(abs_path)

        with self._session() as session:
            session.query(FolderRecord).filter(FolderRecord.id == folder_id).delete()
            session.commit()

    def list_folders(self, parent: str = "") -> List[str]:
        """List all folder paths under parent (directory-based enumeration)."""
        root = self._abs(parent) if parent else self.vault_path
        if not root.is_dir():
            return []
        return [
            str(p.relative_to(self.vault_path)) for p in root.rglob("*") if p.is_dir() and not p.name.startswith(".")
        ]

    def create_folder(self, path: str) -> None:
        """Create a folder directory."""
        self._abs(path).mkdir(parents=True, exist_ok=True)

    def delete_folder(self, path: str) -> None:
        """Delete a folder directory."""
        abs_path = self._abs(path)
        if abs_path.is_dir():
            shutil.rmtree(abs_path)

    def folder_exists(self, path: str) -> bool:
        """Check if a folder directory exists."""
        return self._abs(path).is_dir()

    def move_folder(self, src_path: str, dest_path: str) -> None:
        """Move a folder from src to dest."""
        src = self._abs(src_path)
        dst = self._abs(dest_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    def get_folder_metadata(self, path: str) -> dict:
        """Get folder metadata (timestamps and path info)."""
        abs_path = self._abs(path)
        stat = abs_path.stat()
        return {
            "path": path,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    # ========================================================================
    # Notes
    # ========================================================================

    def save_note(self, note: Note) -> None:
        """Save or update a Note (metadata in DB, content as markdown file)."""
        # Write content to markdown file
        if hasattr(note, "path") and note.path:
            abs_path = self._abs(note.path)
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(note.content, encoding="utf-8")

        # Store metadata in database
        with self._session() as session:
            record = session.query(NoteRecord).filter(NoteRecord.id == note.id).first()
            if record:
                record.data = note.model_dump_json()
            else:
                record = NoteRecord(id=note.id, data=note.model_dump_json())
                session.add(record)
            session.commit()

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """Retrieve a Note by ID."""
        with self._session() as session:
            record = session.query(NoteRecord).filter(NoteRecord.id == note_id).first()
            if record:
                note = Note.model_validate_json(record.data)
                # Load content from file if available
                if hasattr(note, "path") and note.path:
                    abs_path = self._abs(note.path)
                    if abs_path.is_file():
                        note.content = abs_path.read_text(encoding="utf-8")
                return note
        return None

    def delete_note_by_id(self, note_id: str) -> None:
        """Delete a Note by ID."""
        with self._session() as session:
            record = session.query(NoteRecord).filter(NoteRecord.id == note_id).first()
            if record:
                note = Note.model_validate_json(record.data)
                # Delete markdown file
                if hasattr(note, "path") and note.path:
                    abs_path = self._abs(note.path)
                    if abs_path.is_file():
                        abs_path.unlink()

        with self._session() as session:
            session.query(NoteRecord).filter(NoteRecord.id == note_id).delete()
            session.commit()

    def list_notes(self, folder: str = "") -> List[str]:
        """List all markdown note file paths under folder."""
        root = self._abs(folder) if folder else self.vault_path
        if not root.is_dir():
            return []
        return [str(p.relative_to(self.vault_path)) for p in root.rglob("*.md") if p.is_file()]

    def read_note(self, path: str) -> str:
        """Read note content from markdown file."""
        return self._abs(path).read_text(encoding="utf-8")

    def write_note(self, path: str, content: str) -> None:
        """Write note content to markdown file."""
        abs_path = self._abs(path)
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(content, encoding="utf-8")

    def delete_note(self, path: str) -> None:
        """Delete a note markdown file."""
        abs_path = self._abs(path)
        if abs_path.is_file():
            abs_path.unlink()

    def note_exists(self, path: str) -> bool:
        """Check if a note file exists."""
        return self._abs(path).is_file()

    def move_note(self, src_path: str, dest_path: str) -> None:
        """Move a note from src to dest."""
        src = self._abs(src_path)
        dst = self._abs(dest_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    def copy_note(self, src_path: str, dest_path: str) -> None:
        """Copy a note from src to dest."""
        src = self._abs(src_path)
        dst = self._abs(dest_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))

    def get_note_metadata(self, path: str) -> dict:
        """Get note metadata (timestamps and path info)."""
        abs_path = self._abs(path)
        stat = abs_path.stat()
        return {
            "path": path,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    # ========================================================================
    # Characters, Maps, Images, Sounds, Sessions
    # ========================================================================

    def save_character(self, character: Character) -> None:
        """Save or update a Character record."""
        with self._session() as session:
            record = session.query(CharacterRecord).filter(CharacterRecord.id == character.id).first()
            if record:
                record.data = character.model_dump_json()
            else:
                record = CharacterRecord(id=character.id, data=character.model_dump_json())
                session.add(record)
            session.commit()

    def get_character_by_id(self, character_id: str) -> Optional[Character]:
        """Retrieve a Character by ID."""
        with self._session() as session:
            record = session.query(CharacterRecord).filter(CharacterRecord.id == character_id).first()
            if record:
                return Character.model_validate_json(record.data)
        return None

    def delete_character_by_id(self, character_id: str) -> None:
        """Delete a Character by ID."""
        with self._session() as session:
            session.query(CharacterRecord).filter(CharacterRecord.id == character_id).delete()
            session.commit()

    def save_map(self, map_obj: Map) -> None:
        """Save or update a Map record."""
        with self._session() as session:
            record = session.query(MapRecord).filter(MapRecord.id == map_obj.id).first()
            if record:
                record.data = map_obj.model_dump_json()
            else:
                record = MapRecord(id=map_obj.id, data=map_obj.model_dump_json())
                session.add(record)
            session.commit()

    def get_map_by_id(self, map_id: str) -> Optional[Map]:
        """Retrieve a Map by ID."""
        with self._session() as session:
            record = session.query(MapRecord).filter(MapRecord.id == map_id).first()
            if record:
                return Map.model_validate_json(record.data)
        return None

    def delete_map_by_id(self, map_id: str) -> None:
        """Delete a Map by ID."""
        with self._session() as session:
            session.query(MapRecord).filter(MapRecord.id == map_id).delete()
            session.commit()

    def save_image(self, image: Image) -> None:
        """Save or update an Image record."""
        with self._session() as session:
            record = session.query(ImageRecord).filter(ImageRecord.id == image.id).first()
            if record:
                record.data = image.model_dump_json()
            else:
                record = ImageRecord(id=image.id, data=image.model_dump_json())
                session.add(record)
            session.commit()

    def get_image_by_id(self, image_id: str) -> Optional[Image]:
        """Retrieve an Image by ID."""
        with self._session() as session:
            record = session.query(ImageRecord).filter(ImageRecord.id == image_id).first()
            if record:
                return Image.model_validate_json(record.data)
        return None

    def delete_image_by_id(self, image_id: str) -> None:
        """Delete an Image by ID."""
        with self._session() as session:
            session.query(ImageRecord).filter(ImageRecord.id == image_id).delete()
            session.commit()

    def save_sound(self, sound: Sound) -> None:
        """Save or update a Sound record."""
        with self._session() as session:
            record = session.query(SoundRecord).filter(SoundRecord.id == sound.id).first()
            if record:
                record.data = sound.model_dump_json()
            else:
                record = SoundRecord(id=sound.id, data=sound.model_dump_json())
                session.add(record)
            session.commit()

    def get_sound_by_id(self, sound_id: str) -> Optional[Sound]:
        """Retrieve a Sound by ID."""
        with self._session() as session:
            record = session.query(SoundRecord).filter(SoundRecord.id == sound_id).first()
            if record:
                return Sound.model_validate_json(record.data)
        return None

    def delete_sound_by_id(self, sound_id: str) -> None:
        """Delete a Sound by ID."""
        with self._session() as session:
            session.query(SoundRecord).filter(SoundRecord.id == sound_id).delete()
            session.commit()

    def save_session(self, session_obj: SessionModel) -> None:
        """Save or update a Session record."""
        with self._session() as session:
            record = session.query(SessionRecord).filter(SessionRecord.id == session_obj.id).first()
            if record:
                record.data = session_obj.model_dump_json()
            else:
                record = SessionRecord(id=session_obj.id, data=session_obj.model_dump_json())
                session.add(record)
            session.commit()

    def get_session_by_id(self, session_id: str) -> Optional[SessionModel]:
        """Retrieve a Session by ID."""
        with self._session() as session:
            record = session.query(SessionRecord).filter(SessionRecord.id == session_id).first()
            if record:
                return SessionModel.model_validate_json(record.data)
        return None

    def delete_session_by_id(self, session_id: str) -> None:
        """Delete a Session by ID."""
        with self._session() as session:
            session.query(SessionRecord).filter(SessionRecord.id == session_id).delete()
            session.commit()

    # ========================================================================
    # Starred/Favorites
    # ========================================================================

    def read_starred(self) -> Set[str]:
        """Read the set of starred note IDs."""
        with self._session() as session:
            record = session.query(StarredRecord).filter(StarredRecord.id == "1").first()
            if record:
                try:
                    return set(json.loads(record.data))
                except (json.JSONDecodeError, TypeError):
                    return set()
        return set()

    def write_starred(self, stars: Set[str]) -> None:
        """Write the set of starred note IDs."""
        with self._session() as session:
            record = session.query(StarredRecord).filter(StarredRecord.id == "1").first()
            if record:
                record.data = json.dumps(list(stars))
            else:
                record = StarredRecord(id="1", data=json.dumps(list(stars)))
                session.add(record)
            session.commit()

    # ========================================================================
    # Versioning / Backups
    # ========================================================================

    def backup_note(self, note_path: str) -> str:
        """Create a timestamped backup of a note file."""
        orig = self._abs(note_path)
        version_dir = self.vault_path / ".versions" / Path(note_path).parent
        version_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = version_dir / f"{orig.name}.{timestamp}.bak"
        shutil.copy2(str(orig), str(backup))
        return str(backup)

    def list_note_versions(self, note_path: str) -> List[str]:
        """List all backup versions of a note."""
        version_dir = self.vault_path / ".versions" / Path(note_path).parent
        if not version_dir.is_dir():
            return []
        stem = Path(note_path).stem
        return [p.name for p in version_dir.iterdir() if p.name.startswith(stem) and p.suffix == ".bak"]

    def restore_note_version(self, note_path: str, version: str) -> None:
        """Restore a note from a backup version."""
        version_dir = self.vault_path / ".versions" / Path(note_path).parent
        shutil.copy2(str(version_dir / version), str(self._abs(note_path)))

    # ========================================================================
    # Attachments
    # ========================================================================

    def list_attachments(self, folder: str = "") -> List[str]:
        """List all attachments in a folder."""
        path = self.vault_path / "_attachments" / folder
        if not path.is_dir():
            return []
        return [p.name for p in path.iterdir() if p.is_file() and p.suffix != ".md"]

    def add_attachment(self, folder: str, filename: str, data: bytes) -> None:
        """Add an attachment (binary data) to a folder."""
        dest = self.vault_path / "_attachments" / folder / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)

    def delete_attachment(self, path: str) -> None:
        """Delete an attachment."""
        abs_path = self.vault_path / "_attachments" / path
        if abs_path.is_file():
            abs_path.unlink()

    # ========================================================================
    # Search & Existence
    # ========================================================================

    def exists(self, rel_path: str) -> bool:
        """Check if a note or folder exists."""
        return self._abs(rel_path).exists()

    def search_notes(self, query: str, vault_id: str = "", top_k: int = 100) -> List[Note]:
        """
        Full-text search across all markdown notes.

        Case-insensitive substring match on title and content.
        vault_id is accepted for interface compatibility but is ignored
        (all notes in vault_path are searched).
        """
        query_lower = query.lower()
        results: List[Note] = []

        for p in self.vault_path.rglob("*.md"):
            if p.name.startswith("."):
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                if query_lower in p.stem.lower() or query_lower in content.lower():
                    rel = str(p.relative_to(self.vault_path))
                    results.append(
                        Note(
                            id=rel,
                            owner_id="system",
                            vault_id=vault_id or str(self.vault_path),
                            title=p.stem,
                            content=content,
                        )
                    )
                    if len(results) >= top_k:
                        break
            except Exception:
                continue

        return results

    def update_note_metadata(self, note_id: str, meta: dict) -> None:
        """
        Merge meta dict into the stored metadata for note_id.

        Only updates provided keys — does not overwrite the full record.
        """
        with self._session() as session:
            record = session.query(NoteRecord).filter(NoteRecord.id == note_id).first()
            if record:
                existing = json.loads(record.data)
                existing.update(meta)
                record.data = json.dumps(existing)
                session.commit()
