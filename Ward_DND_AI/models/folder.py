import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Folder(BaseModel):
    """
    A folder for organizing notes within a vault/campaign.
    Supports parent/child hierarchy, permissions, and metadata.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique folder ID (UUID4).",
    )
    schema_version: int = Field(default=1, description="Model version for migration/upgrades.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When folder was created.")
    vault_id: str = Field(..., description="Vault/campaign this folder belongs to.")
    parent_id: Optional[str] = Field(default=None, description="ID of parent folder, if any (for nested folders).")
    name: str = Field(..., min_length=1, max_length=128, description="Folder name/title.")
    description: Optional[str] = Field(default=None, description="Folder description or summary (optional).")
    owner_id: str = Field(..., description="User ID who created this folder.")
    group_id: Optional[str] = Field(default=None, description="Group/team with access (if any).")
    permissions: Dict[str, str] = Field(default_factory=dict, description="User/group permissions for this folder.")
    path: Optional[str] = Field(
        default=None,
        description="Relative path within the vault (e.g., 'NPCs/Villains').",
    )
    note_ids: List[str] = Field(default_factory=list, description="IDs of notes in this folder.")
    meta: Dict[str, str] = Field(default_factory=dict, description="Obsidian/YAML or other metadata.")
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp.")
    version: int = Field(default=1, description="Folder revision/version for sync/history.")

    class Config:
        validate_assignment = True
        extra = "forbid"
