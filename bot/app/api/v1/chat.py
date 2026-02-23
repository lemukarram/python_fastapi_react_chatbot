from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.core.db import get_async_session
from app.core.auth import current_active_user
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
        reply = await service.chat(user.id, request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI processing failed.")