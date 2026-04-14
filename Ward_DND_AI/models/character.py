import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Character(BaseModel):
    """
    Represents a character (PC, NPC, monster, etc.) in a campaign.
    Supports stats, notes, player/NPC type, and full extensibility for custom systems.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique character ID (UUID4).",
    )
    schema_version: int = Field(default=1, description="Model version for migrations/upgrades.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When character was created.")
    vault_id: str = Field(..., description="Vault/campaign this character belongs to.")
    name: str = Field(..., min_length=1, max_length=128, description="Character name.")
    description: Optional[str] = Field(default=None, description="Summary, bio, or background.")
    owner_id: str = Field(..., description="User ID who controls/created this character.")
    group_id: Optional[str] = Field(default=None, description="Group/party with access.")
    permissions: Dict[str, str] = Field(default_factory=dict, description="User/group permissions for this character.")
    is_npc: bool = Field(
        default=False,
        description="Is this an NPC? (If False, is a PC/player character.)",
    )
    stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value stats, skills, attributes, HP, etc.",
    )
    tags: List[str] = Field(default_factory=list, description="Tags for search, AI, grouping, etc.")
    notes: List[str] = Field(default_factory=list, description="IDs of note(s) about this character.")
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured extra info, custom fields, YAML, frontmatter, etc.",
    )
    ai_memory: Optional[str] = Field(default=None, description="AI-generated or user-written summary/memory/log.")
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp.")
    version: int = Field(default=1, description="Revision/version for sync/history.")

    class Config:
        validate_assignment = True
        extra = "forbid"
