from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import create_db_and_tables
from app.core.auth import fastapi_users, auth_backend
from app.api.v1 import chat
from app.schemas.user import UserRead, UserCreate

# Create the FastAPI instance
app = FastAPI(
    title="AI Chatbot Pro",
    description="A professional Gemini-powered chatbot with RAG and secure Auth.",
    version="1.0.0"
)

# Setup CORS so your React frontend can talk to this backend
# For local development, we allow all. In production, you'd specify your domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Add Authentication Routes (Login)
# This creates the /auth/jwt/login and /auth/jwt/logout endpoints
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# 2. Add Registration Routes
# This creates the /auth/register endpoint
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# 3. Add the Chat Logic Routes
# This includes the /api/v1/message endpoint we built
app.include_router(
    chat.router,
    prefix="/api/v1",
    tags=["chat"]
)

@app.on_event("startup")
async def on_startup():
    """
    This function runs the moment the server starts.
    It creates the Postgres tables and enables pgvector automatically.
    """
    await create_db_and_tables()

@app.get("/")
async def root():
    """
    A simple health check to see if the API is online.
    """
    return {
        "message": "AI Chatbot API is online and secure.",
        "location": "Riyadh, KSA",
        "developer": "Mukarram Hussain (Tech with muk)"
    }