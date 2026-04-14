import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Vault(BaseModel):
    """
    Represents a campaign/world/project—contains all notes, characters, maps, assets, and settings.
    Swappable: the user can have multiple vaults, switching between games/worlds as needed.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique vault/campaign ID.",
    )
    schema_version: int = Field(default=1, description="Model version for migration/upgrades.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When this vault was created.")
    name: str = Field(..., min_length=2, max_length=64, description="Vault/campaign name.")
    description: Optional[str] = Field(default=None, description="Optional campaign/world summary/about.")
    owner_id: str = Field(..., description="User ID or group ID who owns this vault.")
    members: List[str] = Field(default_factory=list, description="User/group IDs with access to this vault.")
    roles: List[str] = Field(
        default_factory=list,
        description="Optional campaign roles: ['GM', 'player', ...].",
    )
    is_active: bool = Field(default=True, description="Enable/archive this vault/campaign.")
    settings: Dict[str, str] = Field(
        default_factory=dict,
        description="Per-vault config/settings for AI, export, UI, etc.",
    )
    permissions: Dict[str, str] = Field(
        default_factory=dict,
        description="Fine-grained user/group permissions for this vault.",
    )
    version: int = Field(default=1, description="Vault revision/version for sync or upgrade.")

    class Config:
        validate_assignment = True
        extra = "forbid"
