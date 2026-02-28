import uuid
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

# This is the base class that all our tables will inherit from
class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    This table stores your registered users. 
    FastAPI Users handles the email and hashed password automatically.
    """
    pass

class ChatMessage(Base):
    """
    This table stores every single message between the user and the AI.
    It helps the bot remember what was said in previous turns.
    """
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(10)) # Will store 'user' or 'bot'
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

class KnowledgeBase(Base):
    """
    This is your Vector Database table for RAG.
    It stores text snippets and their mathematical 'embeddings'.
    """
    __tablename__ = "knowledge_base"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(Text)
    
    # Gemini embeddings are 768 dimensions. 
    # This column allows Postgres to do high-speed AI searching.
    embedding: Mapped[Vector] = mapped_column(Vector(768))