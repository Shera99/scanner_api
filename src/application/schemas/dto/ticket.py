"""Ticket DTOs."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketDTO(BaseModel):
    """Ticket (OrderItem) data transfer object."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    serial_number: str | None = None
    price: int
    checked: bool = False
    in_out: int = 0
    session_id: int
    is_refund: bool = False
    title: str | None = None
    ticket_type: str | None = None


class TicketListItemDTO(BaseModel):
    """DTO for ticket list item."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    serial_number: str | None = None
    checked: bool = False
    order_status: str | None = None
    ticket_type: str | None = None
    place: str | None = None
    price: int
    qr_number: str | None = None
    user_name: str | None = None
    user_email: str | None = None
    user_phone: str | None = None
    order_date: datetime | None = None
