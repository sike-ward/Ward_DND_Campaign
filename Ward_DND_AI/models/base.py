import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CoreModel(BaseModel):
    """
    Shared base for all data models.
    Provides: unique ID, schema version, creation timestamp, and core config.
    """

    schema_version: int = Field(default=1, const=True, description="Model version for migrations/compatibility.")
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Globally unique UUID for each object.",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp (UTC).")

    class Config:
        validate_assignment = True  # Enforce types/validation on changes
        extra = "forbid"  # Disallow unknown fields for safety
