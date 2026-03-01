import uuid
from datetime import datetime
from pydantic import BaseModel


class AdminUserRead(BaseModel):
    """Schema for listing all users in the admin panel."""
    id: uuid.UUID
    email: str
    is_active: bool
    is_superuser: bool
    message_count: int

    model_config = {"from_attributes": True}


class AdminChatRead(BaseModel):
    """Schema for listing all chat messages across all users."""
    id: uuid.UUID
    user_email: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminKnowledgeRead(BaseModel):
    """Schema for listing knowledge base entries. Embedding is never exposed."""
    id: uuid.UUID
    content_preview: str  # First 200 chars of content only

    model_config = {"from_attributes": True}


class AdminIngestResponse(BaseModel):
    """Schema for the response after file upload ingestion."""
    inserted: int
    message: str
