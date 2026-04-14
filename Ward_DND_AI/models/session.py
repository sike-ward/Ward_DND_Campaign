import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Session(BaseModel):
    """
    Represents a user login session.
    Tracks authentication tokens, expiry, context, and metadata.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session ID (UUID4).",
    )
    schema_version: int = Field(default=1, description="Model schema version for migration.")
    user_id: str = Field(..., description="ID of the user owning this session.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp.")
    expires_at: datetime = Field(..., description="When this session expires.")
    refresh_token: Optional[str] = Field(default=None, description="Token to refresh session.")
    ip_address: Optional[str] = Field(default=None, description="Client IP address.")
    user_agent: Optional[str] = Field(default=None, description="Client user agent string.")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context/state for the session.")
    is_active: bool = Field(default=True, description="Is session currently active.")

    class Config:
        validate_assignment = True
        extra = "forbid"

    def is_expired(self) -> bool:
        """Check if the session is expired."""
        return datetime.utcnow() >= self.expires_at

    def refresh_expiry(self, duration: timedelta):
        """Extend the expiry by the given duration."""
        self.expires_at = datetime.utcnow() + duration
