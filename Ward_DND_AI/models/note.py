import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Note(BaseModel):
    """
    A persistent note for lore, session logs, items, NPCs, locations, etc.
    All notes are scoped to a vault/campaign, with full AI, tags, permissions, and rich metadata support.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique note ID (UUID4).")
    schema_version: int = Field(default=1, description="Model version for migration/upgrades.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When note was created.")
    vault_id: str = Field(..., description="Vault/campaign this note belongs to.")
    folder_id: Optional[str] = Field(default=None, description="Parent folder ID, if any.")
    title: str = Field(..., min_length=1, max_length=128, description="Note title or heading.")
    content: str = Field(default="", description="Markdown/rich text. User, AI, or Obsidian content.")
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for organization/search (user or AI-generated).",
    )
    owner_id: str = Field(..., description="User ID who created this note.")
    group_id: Optional[str] = Field(default=None, description="Group/team ID with edit/view access, if any.")
    permissions: Dict[str, str] = Field(
        default_factory=dict,
        description="User/group permission overrides for this note.",
    )
    links: List[str] = Field(
        default_factory=list,
        description="IDs of notes this note links to (wiki style).",
    )
    attachments: List[str] = Field(
        default_factory=list,
        description="Attached asset IDs (images, sounds, maps, etc).",
    )
    ai_summary: Optional[str] = Field(default=None, description="AI-generated summary or search snippet.")
    meta: Dict[str, str] = Field(default_factory=dict, description="YAML frontmatter/Obsidian compatibility.")
    path: Optional[str] = Field(
        default=None,
        description="Relative path within the vault (e.g., 'NPCs/Aldric.md').",
    )
    note_type: str = Field(
        default="generic",
        description="Type/category: e.g., 'npc', 'item', 'location', 'session', etc.",
    )
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp.")
    version: int = Field(default=1, description="Note revision/version for sync/history.")

    class Config:
        validate_assignment = True
        extra = "forbid"
