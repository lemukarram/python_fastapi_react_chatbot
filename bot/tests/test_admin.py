"""
Tests 6–11 — Admin API Endpoints
"""

import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


# ─────────────────────────────────────────────
# TEST 6: Admin routes require superuser — regular user gets 403
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_admin_requires_superuser(client: AsyncClient, auth_token: str):
    """
    GIVEN a regular (non-superuser) authenticated user
    WHEN  GET /api/v1/admin/users is called
    THEN  the response is 403 Forbidden
    """
    res = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"


# ─────────────────────────────────────────────
# TEST 7: GET /api/v1/admin/users — superuser gets user list
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, superuser_token: str):
    """
    GIVEN a superuser
    WHEN  GET /api/v1/admin/users is called
    THEN  the response is 200 and returns a list with at least the admin user,
          each entry containing required fields
    """
    res = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    user = data[0]
    assert "id" in user
    assert "email" in user
    assert "is_active" in user
    assert "is_superuser" in user
    assert "message_count" in user


# ─────────────────────────────────────────────
# TEST 8: GET /api/v1/admin/chats — superuser gets all chat messages
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_admin_list_chats(client: AsyncClient, superuser_token: str):
    """
    GIVEN a superuser
    WHEN  GET /api/v1/admin/chats is called
    THEN  the response is 200 and returns a list (may be empty)
          with the correct schema when entries exist
    """
    res = await client.get(
        "/api/v1/admin/chats",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert isinstance(data, list)
    if data:
        chat = data[0]
        assert "id" in chat
        assert "user_email" in chat
        assert "role" in chat
        assert "content" in chat
        assert "created_at" in chat


# ─────────────────────────────────────────────
# TEST 9: GET /api/v1/admin/knowledge — superuser gets KB entries
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_admin_list_knowledge(client: AsyncClient, superuser_token: str):
    """
    GIVEN a superuser
    WHEN  GET /api/v1/admin/knowledge is called
    THEN  the response is 200 and returns a list (may be empty),
          entries never expose embedding vectors
    """
    res = await client.get(
        "/api/v1/admin/knowledge",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert isinstance(data, list)
    if data:
        kb = data[0]
        assert "id" in kb
        assert "content_preview" in kb
        assert "embedding" not in kb


# ─────────────────────────────────────────────
# TEST 10: POST /api/v1/admin/knowledge/upload — superuser uploads .txt file
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_admin_upload_txt_file(client: AsyncClient, superuser_token: str):
    """
    GIVEN a superuser with a valid .txt file
    WHEN  POST /api/v1/admin/knowledge/upload is called
    THEN  the response is 200 with inserted count and success message
    """
    file_content = b"Etimad platform requires CR registration.\n\nBid security must be 1%-2% of value."
    res = await client.post(
        "/api/v1/admin/knowledge/upload",
        headers={"Authorization": f"Bearer {superuser_token}"},
        files={"file": ("test_knowledge.txt", file_content, "text/plain")},
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert "inserted" in data
    assert "message" in data
    assert "test_knowledge.txt" in data["message"]


# ─────────────────────────────────────────────
# TEST 11: DELETE /api/v1/admin/knowledge/{id} — superuser deletes KB entry
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_admin_delete_knowledge_entry(client: AsyncClient, superuser_token: str, db_session):
    """
    GIVEN a superuser and an existing KB entry in the database
    WHEN  DELETE /api/v1/admin/knowledge/{entry_id} is called
    THEN  the response is 204 No Content
    AND   a second DELETE returns 404 Not Found
    """
    from sqlalchemy import text

    # Insert directly via raw SQL — SQLite test DB requires a non-NULL embedding;
    # we use a zeroed 768-float blob to satisfy the NOT NULL constraint without pgvector.
    entry_id = uuid.uuid4()
    dummy_embedding = "[" + ",".join(["0.0"] * 768) + "]"
    await db_session.execute(
        text("INSERT INTO knowledge_base (id, content, embedding) VALUES (:id, :content, :emb)"),
        {"id": entry_id.hex, "content": "Test knowledge entry for deletion.", "emb": dummy_embedding},
    )
    await db_session.commit()

    # Delete the entry
    res = await client.delete(
        f"/api/v1/admin/knowledge/{entry_id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert res.status_code == 204, f"Expected 204, got {res.status_code}: {res.text}"

    # Second delete should return 404
    res2 = await client.delete(
        f"/api/v1/admin/knowledge/{entry_id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )
    assert res2.status_code == 404, f"Expected 404 on re-delete, got {res2.status_code}: {res2.text}"
