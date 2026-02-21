from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, 
    service: ChatService = Depends()
):
    reply = await service.chat_with_ai(request.message)
    return ChatResponse(reply=reply)