import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Sound(BaseModel):
    """
    Represents an audio asset for ambient sounds, music, effects.
    Can be linked to notes, scenes, or vaults.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique sound ID (UUID4).",
    )
    schema_version: int = Field(default=1, description="Model schema version for migration.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp.")
    vault_id: str = Field(..., description="Vault/campaign this sound belongs to.")
    owner_id: str = Field(..., description="User ID who uploaded/created the sound.")
    group_id: Optional[str] = Field(default=None, description="Group/party with access.")
    name: str = Field(..., min_length=1, max_length=128, description="Sound title or filename.")
    description: Optional[str] = Field(default=None, description="Description or usage notes.")
    file_path: str = Field(..., description="Path or URL to sound asset file.")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and search.")
    linked_notes: List[str] = Field(default_factory=list, description="Note IDs this sound is attached to.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Extra metadata, e.g., duration, format, etc.")
    is_public: bool = Field(default=True, description="Whether sound is visible to all players.")
    is_deleted: bool = Field(default=False, description="Soft delete flag.")
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Last modification time.")
    version: int = Field(default=1, description="Revision/version number for sync/history.")

    class Config:
        validate_assignment = True
        extra = "forbid"
