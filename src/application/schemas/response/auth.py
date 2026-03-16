"""Auth response schemas."""
from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """User info response."""
    id: int
    email: str | None = None
    phone_number: str | None = None
    full_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AuthResponse(BaseModel):
    """Authentication response."""
    user: UserResponse
    token: str
    role: str
