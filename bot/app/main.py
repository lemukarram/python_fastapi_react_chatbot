import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.db import create_db_and_tables, engine
from app.core.auth import fastapi_users, auth_backend
from app.api.v1.chat import chat_router
from app.schemas.user import UserRead, UserCreate
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT version();"))
        
        await create_db_and_tables()
        
    except Exception as e:
        # We still need to pass the error string to the exception so you get at least some clue
        raise RuntimeError(f"Database startup failed: {str(e)}") from e
        
    yield

app = FastAPI(title=settings.project_name, lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Routes
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

# Chat Routes (Message & History)
app.include_router(
    chat_router, 
    prefix="/api/v1", 
    tags=["chat"]
)

@app.get("/", tags=["system"])
async def root():
    return {
        "status": "online", 
        "message": "AI Tender Assistant is ready.",
        "location": "Jeddah, KSA"
    }