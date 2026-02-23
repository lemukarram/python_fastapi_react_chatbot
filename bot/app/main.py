from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.db import create_db_and_tables, get_async_session, engine
from app.core.auth import fastapi_users, auth_backend, current_active_user
from app.schemas.user import UserRead, UserCreate
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the app starts.
    try:
        print("--- System Check: Tech with muk AI Bot ---")
        
        # Verify exactly which Postgres version we are talking to
        async with engine.connect() as conn:
            version_result = await conn.execute(text("SELECT version();"))
            pg_version = version_result.scalar()
            print(f"Connected to: {pg_version}")
        
        print("Checking database tables and extensions...")
        await create_db_and_tables()
        print("System is ready for users.")
    except Exception as e:
        print(f"Startup Failure: {e}")
    yield
    print("Shutting down...")

app = FastAPI(
    title="AI Chatbot Pro", 
    description="Secure Gemini Chatbot for Riyadh Dev Community",
    lifespan=lifespan
)

# CORS settings for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Routers (JWT & Registration)
app.include_router(
    fastapi_users.get_auth_router(auth_backend), 
    prefix="/auth/jwt", 
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), 
    prefix="/auth", 
    tags=["auth"]
)

@app.post("/api/v1/message", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Private chat endpoint. Only accessible with a valid JWT token.
    """
    service = ChatService(db)
    reply = await service.chat(user.id, request.message)
    return ChatResponse(reply=reply)

@app.get("/")
async def root():
    return {
        "status": "online", 
        "message": "Backend is reachable.",
        "location": "Riyadh, KSA"
    }