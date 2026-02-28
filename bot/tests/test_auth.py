"""
Test 1 & 2 — Authentication: Register and Login
"""

import pytest
from httpx import AsyncClient


# ─────────────────────────────────────────────
# TEST 1: Register a new user successfully
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """
    GIVEN a new email and password
    WHEN  POST /auth/register is called
    THEN  the response is 201 and returns the user's email and id
    """
    res = await client.post("/auth/register", json={
        "email": "newuser@test.com",
        "password": "StrongPass123!"
    })

    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["email"] == "newuser@test.com"
    assert "id" in data
    # Password must never be returned
    assert "password" not in data
    assert "hashed_password" not in data


# ─────────────────────────────────────────────
# TEST 2: Login with valid credentials
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user: dict):
    """
    GIVEN a user who is already registered
    WHEN  POST /auth/jwt/login is called with correct credentials
    THEN  the response is 200 and contains a valid access_token
    """
    res = await client.post(
        "/auth/jwt/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20  # sanity check it's a real token
