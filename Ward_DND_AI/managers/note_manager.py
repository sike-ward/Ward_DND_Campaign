from datetime import datetime
from typing import Dict, List, Optional

from Ward_DND_AI.models.note import Note
from Ward_DND_AI.storage.storage_base import StorageBackend


class NoteManager:
    """
    Handles all business logic and storage operations for Note entities synchronously.
    """

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def create_note(
        self,
        vault_id: str,
        owner_id: str,
        title: str,
        content: str = "",
        folder_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        group_id: Optional[str] = None,
        permissions: Optional[Dict[str, str]] = None,
        links: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        ai_summary: Optional[str] = None,
        meta: Optional[Dict[str, str]] = None,
        note_type: str = "generic",
    ) -> Note:
        """
        Create and store a new note.
        """
        note = Note(
            id=self._generate_id(),
            vault_id=vault_id,
            owner_id=owner_id,
            title=title,
            content=content,
            folder_id=folder_id,
            tags=tags or [],
            group_id=group_id,
            permissions=permissions or {},
            links=links or [],
            attachments=attachments or [],
            ai_summary=ai_summary,
            meta=meta or {},
            note_type=note_type,
            last_modified=datetime.utcnow(),
            created_at=datetime.utcnow(),
            schema_version=1,
            version=1,
        )
        self.storage.save_note(note)
        return note

    def get_note(self, note_id: str) -> Optional[Note]:
        return self.storage.get_note_by_id(note_id)

    def update_note(self, note: Note) -> None:
        note.schema_version = max(note.schema_version, 1)
        note.version += 1
        note.last_modified = datetime.utcnow()
        self.storage.save_note(note)

    def delete_note(self, note_id: str) -> None:
        note = self.get_note(note_id)
        if note:
            # Soft delete: optionally add an is_deleted flag to Note model if needed
            # For now, remove permanently
            self.storage.delete_note_by_id(note_id)

    def add_tag(self, note_id: str, tag: str) -> None:
        note = self.get_note(note_id)
        if note and tag not in note.tags:
            note.tags.append(tag)
            self.update_note(note)

    def remove_tag(self, note_id: str, tag: str) -> None:
        note = self.get_note(note_id)
        if note and tag in note.tags:
            note.tags.remove(tag)
            self.update_note(note)

    def check_permission(self, note_id: str, user_id: str, permission: str) -> bool:
        note = self.get_note(note_id)
        if not note:
            return False
        if "admin" in note.permissions.get(user_id, ""):
            return True
        # Extend permission logic here
        return False

    def _generate_id(self) -> str:
        import uuid

        return str(uuid.uuid4())
