import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Image(BaseModel):
    """
    Stores any image asset (AI-generated art, portrait, handout, scene).
    Not just maps; can be used for scenes, NPCs, items, etc.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique image ID (UUID4).",
    )
    schema_version: int = Field(default=1, description="Model version for migrations.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When image was created.")
    vault_id: str = Field(..., description="Vault/campaign this image belongs to.")
    owner_id: str = Field(..., description="User ID who generated or uploaded this image.")
    file_path: str = Field(..., description="File path or URL to image asset.")
    name: Optional[str] = Field(default=None, description="Title/caption for image (optional).")
    description: Optional[str] = Field(default=None, description="About/context (e.g., 'AI: Village at night').")
    prompt: Optional[str] = Field(default=None, description="AI prompt used, if generated.")
    source: Optional[str] = Field(default=None, description="AI/model name, or 'uploaded'.")
    linked_notes: list = Field(default_factory=list, description="IDs of notes this image is attached to.")
    scene_id: Optional[str] = Field(default=None, description="Scene/session/note ID if generated for one.")
    tags: list = Field(default_factory=list, description="Tags for search, scene type, NPC, item, etc.")
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra metadata (style, rating, AI params, etc.)",
    )
    is_public: bool = Field(default=True, description="Visible to all players?")
    is_deleted: bool = Field(default=False, description="Soft delete for archival.")
    last_modified: datetime = Field(default_factory=datetime.utcnow, description="Last change.")
    version: int = Field(default=1, description="Revision/version for sync/history.")

    class Config:
        validate_assignment = True
        extra = "forbid"
