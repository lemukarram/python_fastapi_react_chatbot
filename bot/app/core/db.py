from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.models.models import User, Base, KnowledgeBase

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    """
    Ensures pgvector is enabled and creates tables.
    If pgvector is missing, it skips the vector table so the app doesn't crash.
    """
    vector_available = False
    
    # Step 1: Try to enable the extension
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("Successfully enabled pgvector extension.")
        vector_available = True
    except Exception as e:
        print("Warning: pgvector extension not found on this system. RAG features will be disabled.")

    # Step 2: Create tables
    async with engine.begin() as conn:
        if vector_available:
            # Create everything if vector is ready
            await conn.run_sync(Base.metadata.create_all)
            print("All database tables (including RAG) created successfully.")
        else:
            # If no vector, we avoid creating the KnowledgeBase table to prevent a crash
            def create_tables_selective(target_base, connection):
                for table in target_base.metadata.sorted_tables:
                    if table.name != "knowledge_base":
                        table.create(connection, checkfirst=True)
            
            await conn.run_sync(lambda sync_conn: create_tables_selective(Base, sync_conn))
            print("Standard tables created. KnowledgeBase skipped due to missing pgvector.")

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)