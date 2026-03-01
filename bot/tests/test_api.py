"""
Test 3, 4 & 5 — API Endpoints: /history, /message, /ingest
"""

import pytest
from httpx import AsyncClient


# ─────────────────────────────────────────────
# TEST 3: GET /api/v1/history — returns empty list for new user
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_history_empty_for_new_user(client: AsyncClient, auth_token: str):
    """
    GIVEN a freshly registered user with no messages yet
    WHEN  GET /api/v1/history is called with a valid token
    THEN  the response is 200 and returns an empty list
    """
    res = await client.get(
        "/api/v1/history",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 0


# ─────────────────────────────────────────────
# TEST 4: POST /api/v1/message — returns a reply and sources
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_send_message_returns_reply(client: AsyncClient, auth_token: str):
    """
    GIVEN a logged-in user
    WHEN  POST /api/v1/message is called with a message
    THEN  the response is 200, contains a 'reply' string and a 'sources' list,
          and the reply matches the mocked AI response
    """
    res = await client.post(
        "/api/v1/message",
        json={"message": "What are the bid security requirements?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert "reply" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert data["reply"] == "Mocked AI reply for testing."


# ─────────────────────────────────────────────
# TEST 5a: POST /api/v1/ingest — regular user is FORBIDDEN (403)
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_ingest_requires_superuser(client: AsyncClient, auth_token: str):
    """
    GIVEN a regular (non-superuser) logged-in user
    WHEN  POST /api/v1/ingest is called
    THEN  the response is 403 Forbidden (ingest is now admin-only)
    """
    res = await client.post(
        "/api/v1/ingest",
        json={"texts": ["Some knowledge text."]},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"


# ─────────────────────────────────────────────
# TEST 5b: POST /api/v1/ingest — superuser can ingest chunks
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_ingest_documents(client: AsyncClient, superuser_token: str):
    """
    GIVEN a superuser (admin)
    WHEN  POST /api/v1/ingest is called with a list of text chunks
    THEN  the response is 200, 'inserted' count matches the number of chunks sent,
          and the success message is returned
    """
    chunks = [
        "Etimad platform requires CR registration before bidding.",
        "Bid security must be between 1% and 2% of the total tender value.",
    ]

    res = await client.post(
        "/api/v1/ingest",
        json={"texts": chunks},
        headers={"Authorization": f"Bearer {superuser_token}"}
    )

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert "inserted" in data
    assert "message" in data
    # RAG ingest_texts is mocked to return 2
    assert data["inserted"] == 2
    assert "Successfully inserted" in data["message"]
