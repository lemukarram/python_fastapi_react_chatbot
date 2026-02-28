from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.models.models import User, Base

# Create the engine to talk to Postgres
engine = create_async_engine(settings.database_url.unicode_string())

# This creates the session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    """
    This function activates the pgvector extension and creates your tables.
    Since the extension is available on your Mac, this will now work.
    """
    # Step 1: Activate pgvector in its own transaction
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("Success: pgvector extension is now active in your database.")
    except Exception as e:
        print(f"Extension Warning: {e}")

    # Step 2: Create all tables (User, ChatMessage, KnowledgeBase)
    # Now that vector is active, the KnowledgeBase table won't crash.
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Success: All database tables created correctly.")
    except Exception as e:
        print(f"Table Creation Error: {e}")
        print("Tip: If it still says 'type vector does not exist', try restarting your terminal.")

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Helper to get a database session for your API routes.
    """
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Connects FastAPI Users to your Postgres database.
    """
    yield SQLAlchemyUserDatabase(session, User)