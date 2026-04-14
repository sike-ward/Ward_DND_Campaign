import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Group(BaseModel):
    """
    A multiplayer group/campaign/party for shared notes, permissions, and collaboration.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique group ID (UUID4).",
    )
    schema_version: int = Field(default=1, description="Model version for migrations.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When group was created.")
    name: str = Field(..., min_length=2, max_length=64, description="Group/campaign/party name.")
    description: Optional[str] = Field(default=None, description="Optional summary/about field.")
    members: List[str] = Field(default_factory=list, description="User IDs in this group.")
    roles: List[str] = Field(default_factory=list, description="Group roles (e.g., admin, player).")
    created_by: str = Field(..., description="User ID who created this group.")
    is_active: bool = Field(default=True, description="Archive/disable group/campaign.")

    class Config:
        validate_assignment = True
        extra = "forbid"
