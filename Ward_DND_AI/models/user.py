import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """
    A user account for the app.
    Supports multiplayer, roles, permissions, and secure login.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique user ID (UUID4).")
    schema_version: int = Field(default=1, description="Model version for migrations.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When account was created.")
    email: EmailStr = Field(..., description="Unique email address, used for login.")
    username: str = Field(..., min_length=3, max_length=32, description="Display name (can be changed).")
    password_hash: str = Field(..., min_length=10, description="Bcrypt/argon2 hash of password.")
    groups: List[str] = Field(default_factory=list, description="Group/party IDs this user is in.")
    roles: List[str] = Field(default_factory=list, description="Role names (e.g., player, GM, admin).")
    is_active: bool = Field(default=True, description="Enable/disable account.")
    last_login: Optional[datetime] = Field(default=None, description="Most recent login timestamp.")

    class Config:
        validate_assignment = True
        extra = "forbid"
