import uuid
from typing import List

import fitz  # PyMuPDF
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import current_superuser
from app.core.db import get_async_session
from app.models.models import User, ChatMessage, KnowledgeBase
from app.schemas.admin import (
    AdminUserRead,
    AdminChatRead,
    AdminKnowledgeRead,
    AdminIngestResponse,
)
from app.services.rag_service import RAGService

admin_router = APIRouter()


# ── GET /api/v1/admin/users ──────────────────────────────────────────────────
@admin_router.get("/users", response_model=List[AdminUserRead])
async def list_users(
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Returns all registered users with their total message count."""
    msg_count_sub = (
        select(ChatMessage.user_id, func.count(ChatMessage.id).label("cnt"))
        .group_by(ChatMessage.user_id)
        .subquery()
    )
    stmt = (
        select(User, func.coalesce(msg_count_sub.c.cnt, 0).label("message_count"))
        .outerjoin(msg_count_sub, User.id == msg_count_sub.c.user_id)
        .order_by(User.email)
    )
    rows = (await db.execute(stmt)).all()
    return [
        AdminUserRead(
            id=row.User.id,
            email=row.User.email,
            is_active=row.User.is_active,
            is_superuser=row.User.is_superuser,
            message_count=row.message_count,
        )
        for row in rows
    ]


# ── GET /api/v1/admin/chats ──────────────────────────────────────────────────
@admin_router.get("/chats", response_model=List[AdminChatRead])
async def list_chats(
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Returns all chat messages across all users, newest first."""
    stmt = (
        select(ChatMessage, User.email)
        .join(User, ChatMessage.user_id == User.id)
        .order_by(ChatMessage.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()
    return [
        AdminChatRead(
            id=row.ChatMessage.id,
            user_email=row.email,
            role=row.ChatMessage.role,
            content=row.ChatMessage.content,
            created_at=row.ChatMessage.created_at,
        )
        for row in rows
    ]


# ── GET /api/v1/admin/knowledge ──────────────────────────────────────────────
@admin_router.get("/knowledge", response_model=List[AdminKnowledgeRead])
async def list_knowledge(
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Returns all knowledge base entries with a 200-char content preview. Embeddings are never sent."""
    stmt = select(KnowledgeBase.id, KnowledgeBase.content).order_by(KnowledgeBase.id)
    rows = (await db.execute(stmt)).all()
    return [
        AdminKnowledgeRead(id=row.id, content_preview=row.content[:200])
        for row in rows
    ]


# ── POST /api/v1/admin/knowledge/upload ──────────────────────────────────────
# NOTE: This route is registered BEFORE /knowledge/{entry_id} so FastAPI does
# not mistake the literal string "upload" for a UUID path parameter.
@admin_router.post("/knowledge/upload", response_model=AdminIngestResponse)
async def upload_knowledge(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """
    Accepts a .txt or .pdf file, extracts its text, splits into chunks on
    double newlines, and ingests each chunk into the knowledge base via RAGService.
    """
    filename = file.filename or ""
    if not (filename.endswith(".txt") or filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are accepted.")

    raw_bytes = await file.read()

    if filename.endswith(".txt"):
        text = raw_bytes.decode("utf-8", errors="replace")
    else:
        # Parse PDF in-memory — no temp files written to disk
        pdf = fitz.open(stream=raw_bytes, filetype="pdf")
        pages = [page.get_text() for page in pdf]
        text = "\n".join(pages)
        pdf.close()

    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    if not chunks:
        raise HTTPException(status_code=422, detail="No text content could be extracted from the file.")

    rag = RAGService()
    inserted = await rag.ingest_texts(db, chunks)
    return AdminIngestResponse(
        inserted=inserted,
        message=f"Uploaded '{filename}' and ingested {inserted} of {len(chunks)} chunk(s) into the knowledge base.",
    )


# ── DELETE /api/v1/admin/knowledge/{entry_id} ────────────────────────────────
@admin_router.delete("/knowledge/{entry_id}", status_code=204)
async def delete_knowledge(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser),
):
    """Deletes a single knowledge base entry by ID. Returns 204 No Content on success."""
    stmt = delete(KnowledgeBase).where(KnowledgeBase.id == entry_id)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found.")
