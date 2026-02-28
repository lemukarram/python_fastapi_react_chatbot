"""
conftest.py — Shared fixtures for all tests.

Strategy:
- Uses an in-memory SQLite database so tests never touch your real Postgres DB.
- Mocks out the Gemini AI and RAG service so tests are fast and don't need API keys.
- Provides a ready-to-use AsyncClient and a helper to register+login a user.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.db import get_async_session
from app.models.models import Base


# ---------------------------------------------------------------------------
# In-memory SQLite engine (isolated per test session, no Postgres needed)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionMaker = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    """Create all tables once before any test runs, drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session():
    """Provides a clean DB session for each test, rolled back after."""
    async with TestSessionMaker() as session:
        yield session


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession):
    """
    AsyncClient wired to the FastAPI app with:
    - DB overridden to use the in-memory SQLite session
    - Gemini AI mocked to return a fixed reply
    - RAG service mocked to return empty sources
    """
    async def override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    # Mock Gemini so tests never call the real API
    with patch(
        "app.providers.gemini.GeminiProvider.get_response",
        new_callable=AsyncMock,
        return_value="Mocked AI reply for testing."
    ):
        # Mock RAG so tests never need pgvector or embeddings
        with patch(
            "app.services.rag_service.RAGService.search_context",
            new_callable=AsyncMock,
            return_value=[]
        ):
            with patch(
                "app.services.rag_service.RAGService.ingest_texts",
                new_callable=AsyncMock,
                return_value=2
            ):
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as ac:
                    yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def registered_user(client: AsyncClient):
    """Registers a test user and returns their credentials."""
    payload = {"email": "mukarram@test.com", "password": "StrongPass123!"}
    await client.post("/auth/register", json=payload)
    return payload


@pytest_asyncio.fixture()
async def auth_token(client: AsyncClient, registered_user: dict):
    """Logs in the registered test user and returns the Bearer token."""
    res = await client.post(
        "/auth/jwt/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return res.json()["access_token"]
