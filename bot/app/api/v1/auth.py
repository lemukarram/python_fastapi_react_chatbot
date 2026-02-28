import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from app.core.db import get_user_db
from app.models.models import User
from app.core.config import settings

# This tells the browser/React how to send the token (via the Authorization header).
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    """
    Handles the creation and validation of the JSON Web Token (JWT).
    The lifetime is set to 1 hour (3600 seconds).
    """
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=3600)

# This combines the transport and the strategy into a single backend.
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    This class handles user lifecycle events like registration and password resets.
    """
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

async def get_user_manager(user_db=Depends(get_user_db)):
    """
    A helper function to get the user manager instance for our routes.
    """
    yield UserManager(user_db)

# The main FastAPI Users object. We use this to generate our login/register routes.
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# This is the 'guard' you will use in your chat routes to make them private.
current_active_user = fastapi_users.current_user(active=True)