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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("--- Starting Tech with muk AI Bot ---")
    try:
        async with engine.connect() as conn:
            version_result = await conn.execute(text("SELECT version();"))
            logger.info(f"Connected to: {version_result.scalar()}")
        
        await create_db_and_tables()
        logger.info("Database tables are ready.")
    except Exception as e:
        logger.error(f"Startup Failure: {str(e)}")
    yield
    logger.info("--- Shutting down ---")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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