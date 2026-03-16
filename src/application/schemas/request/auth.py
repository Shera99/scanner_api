"""Auth request schemas."""
from pydantic import BaseModel, EmailStr, Field


class AuthRequest(BaseModel):
    """Authentication request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
