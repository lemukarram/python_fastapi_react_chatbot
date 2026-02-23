import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.db import create_db_and_tables, get_async_session, engine
from app.core.auth import fastapi_users, auth_backend, current_active_user
from app.schemas.user import UserRead, UserCreate
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.core.config import settings

# Setup basic logging for your 'Tech with muk' debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the startup and shutdown sequence of the application.
    This is where we verify the database connection and setup tables.
    """
    logger.info("--- Starting Tech with muk AI Bot ---")
    try:
        # 1. Verify PostgreSQL connection and version
        async with engine.connect() as conn:
            version_result = await conn.execute(text("SELECT version();"))
            pg_version = version_result.scalar()
            logger.info(f"Connected to: {pg_version}")
        
        # 2. Run database migrations / table creation
        logger.info("Initializing database tables...")
        await create_db_and_tables()
        logger.info("Database is fully synchronized.")
        
    except Exception as e:
        logger.error(f"Startup Failure: {str(e)}")
        # We don't stop the app here so you can still check logs via the API
    
    yield
    logger.info("--- Shutting down Tech with muk AI Bot ---")

# App Initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Secure Gemini 2.0 Chatbot with RAG and PostgreSQL support.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# In production, replace ["*"] with your actual frontend URL (e.g., your Riyadh domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Routes ---
# JWT Login/Logout
app.include_router(
    fastapi_users.get_auth_router(auth_backend), 
    prefix="/auth/jwt", 
    tags=["auth"]
)

# User Registration
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), 
    prefix="/auth", 
    tags=["auth"]
)

# --- Chat Logic ---
@app.post("/api/v1/message", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Main Chat API. 
    - Requires JWT token (current_active_user).
    - Uses database session for chat history and RAG search.
    """
    try:
        service = ChatService(db)
        # We pass the authenticated user.id to keep conversations private
        reply = await service.chat(user.id, request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"Chat error for user {user.id}: {e}")
        raise HTTPException(status_code=500, detail="The AI assistant is currently unavailable.")

# --- Health Check ---
@app.get("/", tags=["system"])
async def root():
    """
    Simple status check to verify the API is alive.
    """
    return {
        "status": "online",
        "message": "AI Chatbot API is reachable.",
        "location": "Riyadh, KSA",
        "developer": "Mukarram Hussain (Tech with muk)"
    }