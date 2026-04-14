import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Map(BaseModel):
    """
    Represents a map asset (image, grid, handout) for a campaign.
    Supports linking to notes, folders, AI, and rich metadata.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique map ID (UUID4).")
    schema_version: int = Field(default=1, description="Model version for migrations/upgrades.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When map was created.")
    vault_id: str = Field(..., description="Vault/campaign this map belongs to.")
    owner_id: str = Field(..., description="User ID who uploaded/created this map.")
    group_id: Optional[str] = Field(default=None, description="Group/party with access.")
    name: str = Field(..., min_length=1, max_length=128, description="Map title (for display/search).")
    description: Optional[str] = Field(default=None, description="Map summary/about field.")
    file_path: str = Field(..., description="Relative or absolute file path to map asset/image.")
    permissions: Dict[str, str] = Field(default_factory=dict, description="User/group permissions for this map.")
    tags: List[str] = Field(default_factory=list, description="Tags for search, AI, UI grouping, etc.")
    linked_notes: List[str] = Field(
        default_factory=list,
        description="Note IDs this map links to (for lore, context, AI).",
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra metadata (grid, scale, custom fields, etc).",
    )
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp.")
    version: int = Field(default=1, description="Revision/version for sync/history.")

    class Config:
        validate_assignment = True
        extra = "forbid"
