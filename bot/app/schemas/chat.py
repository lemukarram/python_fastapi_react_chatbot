from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    """
    Schema for messages sent from your React app.
    """
    message: str = Field(..., json_schema_extra={"example": "What is the weather like in Riyadh?"})

    # Even though we use User ID from the token, we keep session_id
    # here in case you want to handle specific chat threads later.
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """
    Schema for the response sent back to the user.
    """
    reply: str

    # This list will store text snippets found during the RAG search.
    # It shows the user that the AI is using your custom data.
    sources: Optional[List[str]] = Field(default_factory=list)

class IngestRequest(BaseModel):
    """
    Schema for adding a document/text chunk into the knowledge base.
    Send one or more plain-text chunks; each will be embedded and stored.
    """
    texts: List[str] = Field(..., json_schema_extra={"example": ["Etimad platform requires CR registration before bidding."]})

class IngestResponse(BaseModel):
    """
    Schema for the response after ingesting documents.
    """
    inserted: int
    message: str