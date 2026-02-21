from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    """
    Schema for incoming chat messages.
    """
    message: str = Field(..., example="How is the weather in Riyadh?")
    # You can add more fields here later, like session_id or user_id
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """
    Schema for the chatbot's response.
    """
    reply: str
    # In the future, you can add sources here for RAG
    sources: Optional[List[str]] = None