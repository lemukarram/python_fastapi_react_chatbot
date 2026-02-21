from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, 
    service: ChatService = Depends()
):
    # We take the session_id from the request (sent by React)
    # If React doesn't send one, it defaults to "default"
    session_id = request.session_id or "default"

    reply = await service.chat_with_ai(request.message, session_id=session_id)
    return ChatResponse(reply=reply)