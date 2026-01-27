from app.database import db
from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token
from typing import Optional


async def create_user(email: str, name: str, password: str) -> User:
    """Create a new user."""
    hashed = hash_password(password)
    user = User(email=email, name=name, password_hash=hashed)
    await db.users.insert_one(user.model_dump(by_alias=True))
    return user


async def authenticate_user(email: str, password: str) -> Optional[str]:
    """Authenticate a user and return JWT token."""
    user_data = await db.users.find_one({"email": email})
    if not user_data:
        return None

    user = User(**user_data)
    if not verify_password(password, user.password_hash):
        return None

    # Create access token with user_id in the 'sub' claim
    token = create_access_token(data={"sub": user.id})
    return token
