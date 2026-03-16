"""Event DTOs."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventDTO(BaseModel):
    """Event data transfer object."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str | None = None
    image_path: str | None = None
    category_id: int | None = None


class SessionDTO(BaseModel):
    """Session data transfer object."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    event_id: int
    date_time: datetime
    all_tickets_count: int = 0
    scanned_tickets_count: int = 0
    scanned_in_tickets_count: int = 0
    scanned_out_tickets_count: int = 0
