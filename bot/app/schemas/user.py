import uuid
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    """
    This schema defines the data returned when reading a user.
    It includes the ID and email but excludes the password.
    """
    pass

class UserCreate(schemas.BaseUserCreate):
    """
    This schema is used when a new user registers.
    It requires an email and a password.
    """
    pass

class UserUpdate(schemas.BaseUserUpdate):
    """
    This schema allows users to update their information later.
    """
    pass