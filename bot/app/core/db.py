from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.models.models import User

# Create the async engine to talk to Postgres
engine = create_async_engine(settings.database_url.unicode_string())

# This creates the session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

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
