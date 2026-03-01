from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.chat import ChatRequest, ChatResponse, IngestRequest, IngestResponse
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app.core.db import get_async_session
from app.core.auth import current_active_user, current_superuser
from app.models.models import User

chat_router = APIRouter()

@chat_router.get("/history", response_model=List[dict])
async def get_chat_history(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Fetches the full chat history for the logged-in user.
    """
    try:
        service = ChatService(db)
        return await service.get_history(user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not load chat history.")

@chat_router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Processes the chat message through the AI.
    """
    try:
        service = ChatService(db)
        result = await service.chat(user.id, request.message)
        # We pass both fields to the ChatResponse schema
        return ChatResponse(
            reply=result.get("reply", "No response generated."),
            sources=result.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI processing failed.")

@chat_router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser)
):
    """
    Ingests one or more text chunks into the knowledge base.
    Each chunk is embedded via Gemini and stored in the vector DB.
    Requires superuser (admin) privileges.
    """
    try:
        rag = RAGService()
        inserted = await rag.ingest_texts(db, request.texts)
        return IngestResponse(
            inserted=inserted,
            message=f"Successfully inserted {inserted} of {len(request.texts)} chunk(s) into the knowledge base."
        )
    except Exception as e:
        print(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest documents.")