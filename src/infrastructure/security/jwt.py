"""Security utilities for JWT tokens and password hashing."""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from pydantic import BaseModel

from src.core.config import settings


class TokenData(BaseModel):
    """Token payload data."""
    id: int
    permission_id: int | None = None
    phone_number: str | None = None
    uid: str | None = None


def check_password(password: str, hashed: str) -> bool:
    """Verify password against hashed password."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_hashed_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict[str, Any]) -> str:
    """Create JWT access token."""
    payload = {
        **data,
        "iss": settings.jwt_issuer,
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=settings.access_token_expire_days),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""
    return jwt.decode(
        token,
        settings.secret_key,
        options={"require": ["exp", "iss"]},
        issuer=settings.jwt_issuer,
        algorithms=[settings.jwt_algorithm],
    )
