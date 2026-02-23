from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.core.db import get_async_session
from app.core.auth import current_active_user
from app.models.models import User

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Handles incoming messages for authenticated users.
    It uses the user's unique ID to manage private chat history and RAG context.
    """
    # We initialize the ChatService with the current database session
    service = ChatService(db)
    
    # We use the authenticated user's ID as the session identifier
    # This ensures that User A never sees User B's chat history
    reply = await service.chat(user.id, request.message)
    
    return ChatResponse(reply=reply)