"""User DTOs."""
from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    """User data transfer object."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str | None = None
    phone_number: str | None = None
    full_name: str | None = None


class PermissionDTO(BaseModel):
    """User permission data transfer object."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    role: str
    event_id: int | None = None
    session_id: int | None = None
    organization_id: int | None = None
    country_id: int | None = None
    theater_id: int | None = None
    is_invitations_enabled: bool = True
