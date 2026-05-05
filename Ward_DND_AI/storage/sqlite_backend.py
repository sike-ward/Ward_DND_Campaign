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
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

from sqlalchemy import Integer, String, Text, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# Mapped is in sqlalchemy.orm, not sqlalchemy.types
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
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class VaultRecord(Base):
    """ORM model for Vault data — stored as JSON blob."""

    __tablename__ = "vaults"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    members_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class FolderRecord(Base):
    """ORM model for Folder data — stored as JSON blob."""

    __tablename__ = "folders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    vault_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob


class NoteRecord(Base):
    """ORM model for Note metadata — content stored as file.

    path is the bridge key linking DB records to filesystem files. Every call
    to write_note() upserts a row keyed on path, so ownership and permissions
    are always in sync with the actual files on disk.

    Permissions model
    -----------------
    permissions_json : JSON array of {"user_id": str, "role": "viewer"|"owner"}
    is_dm_only       : overrides all grants — only admins see it
    is_public        : DM shortcut to share with all players at once
    """

    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="")
    vault_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    # Bridge key — vault-relative path (forward-slash normalised), indexed
    path: Mapped[str] = mapped_column(Text, nullable=False, index=True, default="")
    title: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    permissions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    note_type: Mapped[str] = mapped_column(Text, nullable=False, default="note")
    is_dm_only: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_public: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    linked_note_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    campaign_id: Mapped[str] = mapped_column(Text, nullable=False, default="")
    data: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # spare JSON blob


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
    """Per-user starred note paths — one row per user_id (or 'system' fallback)."""

    __tablename__ = "starred"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # user_id
    data: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON array of paths


# ============================================================================
# Content-extraction helpers (module-level, no storage dependency)
# ============================================================================

_YAML_FRONT_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)
_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_HASHTAG_RE = re.compile(r"(?<!\[)#([A-Za-z0-9_\-]+)")
_WIKILINK_RE = re.compile(r"\[\[([^\[\]|#]+?)(?:[|#][^\[\]]*)?\]\]")


def _extract_title(path: str, content: str) -> str:
    """Return the first H1 heading from content, or the filename stem as fallback."""
    m = _H1_RE.search(content)
    return m.group(1).strip() if m else Path(path).stem


def _extract_tags(content: str) -> list:
    """Return a sorted, deduplicated tag list pulled from three sources:
    1. YAML frontmatter ``tags:`` field (inline list, block list, or scalar).
    2. [[wikilinks]] in the note body.
    3. #hashtags in the note body.
    """
    tags: set = set()

    fm = _YAML_FRONT_RE.match(content)
    body_start = fm.end() if fm else 0

    if fm:
        lines = fm.group(1).splitlines()
        in_tags_block = False
        for line in lines:
            stripped = line.strip()
            if stripped.lower().startswith("tags:"):
                raw = stripped[5:].strip()
                in_tags_block = False
                if raw.startswith("["):
                    # Inline list: tags: [dragon, npc]
                    for t in raw.strip("[]").split(","):
                        t = t.strip().strip("\"'")
                        if t:
                            tags.add(t)
                elif raw:
                    # Scalar: tags: dragon
                    tags.add(raw.strip("\"'"))
                else:
                    # Block list follows on subsequent lines
                    in_tags_block = True
            elif in_tags_block:
                if stripped.startswith("- "):
                    t = stripped[2:].strip().strip("\"'")
                    if t:
                        tags.add(t)
                elif stripped and not stripped.startswith("#"):
                    in_tags_block = False  # end of block

    body = content[body_start:]
    for m in _WIKILINK_RE.finditer(body):
        tags.add(m.group(1).strip())
    for m in _HASHTAG_RE.finditer(body):
        tags.add(m.group(1))

    return sorted(tags)


def _extract_links(content: str) -> list:
    """Return sorted list of [[wikilink]] targets found outside frontmatter."""
    fm = _YAML_FRONT_RE.match(content)
    body = content[fm.end() :] if fm else content
    return sorted({m.group(1).strip() for m in _WIKILINK_RE.finditer(body)})


def _count_words(content: str) -> int:
    """Approximate word count on the note body (frontmatter excluded)."""
    fm = _YAML_FRONT_RE.match(content)
    body = content[fm.end() :] if fm else content
    return len(body.split())


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

        # Create all tables on first run, then apply additive column migrations
        Base.metadata.create_all(self.engine)
        self._apply_schema_migrations()

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

    def _apply_schema_migrations(self) -> None:
        """Add columns introduced in later schema versions to existing databases.

        Only additive ALTER TABLE ADD COLUMN operations are used — safe for
        SQLite and idempotent (skips columns that already exist).
        """
        note_additions: dict = {
            "path": "TEXT NOT NULL DEFAULT ''",
            "title": "TEXT NOT NULL DEFAULT ''",
            "tags_json": "TEXT NOT NULL DEFAULT '[]'",
            "permissions_json": "TEXT NOT NULL DEFAULT '[]'",
            "created_at": "TEXT NOT NULL DEFAULT ''",
            "updated_at": "TEXT NOT NULL DEFAULT ''",
            "note_type": "TEXT NOT NULL DEFAULT 'note'",
            "is_dm_only": "INTEGER NOT NULL DEFAULT 0",
            "is_public": "INTEGER NOT NULL DEFAULT 0",
            "word_count": "INTEGER NOT NULL DEFAULT 0",
            "linked_note_ids": "TEXT NOT NULL DEFAULT '[]'",
            "campaign_id": "TEXT NOT NULL DEFAULT ''",
        }
        with self.engine.connect() as conn:
            existing = {row[1] for row in conn.execute(text("PRAGMA table_info(notes)"))}
            for col, typedef in note_additions.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE notes ADD COLUMN {col} {typedef}"))
            conn.commit()

    def _can_access_note(self, rec: "NoteRecord") -> bool:
        """Return True if the current user may read this note record.

        Rules (evaluated in order):
          1. Admins always have access.
          2. is_dm_only=1  →  only admins; all players denied regardless of other flags.
          3. owner_id == current user  →  access granted.
          4. is_public=1  →  any authenticated player has access.
          5. Explicit viewer/owner grant in permissions_json  →  access granted.
          6. Default: deny.
        """
        if self._is_admin:
            return True
        if rec.is_dm_only:
            return False  # DM-only overrides everything for players
        uid = self._current_user_id
        if not uid:
            return False
        if rec.owner_id == uid:
            return True
        if rec.is_public:
            return True
        try:
            perms = json.loads(rec.permissions_json or "[]")
            return any(p.get("user_id") == uid for p in perms)
        except (json.JSONDecodeError, TypeError):
            return False

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
                record.owner_id = group.owner_id
                record.data = group.model_dump_json()
            else:
                record = GroupRecord(id=group.id, owner_id=group.owner_id, data=group.model_dump_json())
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
                record.owner_id = vault.owner_id
                record.members_json = json.dumps(vault.members)
                record.data = vault.model_dump_json()
            else:
                record = VaultRecord(
                    id=vault.id,
                    owner_id=vault.owner_id,
                    members_json=json.dumps(vault.members),
                    data=vault.model_dump_json(),
                )
                session.add(record)
            session.commit()

    def get_vault_by_id(self, vault_id: str) -> Optional[Vault]:
        """Retrieve a Vault by ID — returns None if user lacks access."""
        with self._session() as session:
            record = session.query(VaultRecord).filter(VaultRecord.id == vault_id).first()
            if record:
                vault = Vault.model_validate_json(record.data)
                members = json.loads(record.members_json or "[]")
                if not self._can_access(vault.owner_id, vault.permissions, members):
                    return None
                return vault
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
                record.owner_id = note.owner_id
                record.vault_id = note.vault_id
                record.data = note.model_dump_json()
            else:
                record = NoteRecord(
                    id=note.id, owner_id=note.owner_id, vault_id=note.vault_id, data=note.model_dump_json()
                )
                session.add(record)
            session.commit()

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """Retrieve a Note by ID — returns None if user lacks access."""
        with self._session() as session:
            record = session.query(NoteRecord).filter(NoteRecord.id == note_id).first()
            if record:
                note = Note.model_validate_json(record.data)
                if not self._can_access(note.owner_id, note.permissions):
                    return None
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
        """List note file paths the current user can access.

        Admins see all notes. Regular users see notes they own
        or notes explicitly shared with them.
        """
        root = self._abs(folder) if folder else self.vault_path
        if not root.is_dir():
            return []
        all_paths = [str(p.relative_to(self.vault_path)) for p in root.rglob("*.md") if p.is_file()]

        if self._is_admin or not self._current_user_id:
            return all_paths

        # Build a set of forward-slash-normalised paths from DB records accessible to this user.
        # NoteRecord has no path column — the path lives inside the JSON data blob.
        accessible_paths: set[str] = set()
        uid = self._current_user_id
        with self._session() as session:
            records = session.query(NoteRecord).filter(NoteRecord.owner_id == uid).all()
            for rec in records:
                note_data = json.loads(rec.data or "{}")
                perms = note_data.get("permissions", {})
                note_path = note_data.get("path", "")
                if note_path and self._can_access(rec.owner_id, perms):
                    accessible_paths.add(note_path.replace("\\", "/"))

        return [p for p in all_paths if p.replace("\\", "/") in accessible_paths]

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
        Merge meta into the stored JSON metadata for note_id.
        Only updates the provided keys; non-overlapping keys are preserved.
        """
        with Session(self.engine) as session:
            record = session.scalar(select(NoteRecord).where(NoteRecord.record_id == note_id))
            if record:
                existing = {}
                try:
                    existing = __import__("json").loads(record.data) if record.data else {}
                except Exception:
                    pass
                existing.update(meta)
                record.data = __import__("json").dumps(existing)
