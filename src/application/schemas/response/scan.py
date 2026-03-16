"""Scan response schemas."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class EventListItem(BaseModel):
    """Event item in list response."""
    id: int
    event_id: int
    event_name: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    image: str | None = None
    date_time: datetime
    all_count: int = 0
    scan_count: int = 0
    theater_name: str | None = None
    address: str | None = None
    inCount: int = 0
    outCount: int = 0


class EventListResponse(BaseModel):
    """Events list response."""
    events: list[EventListItem]


class ScanCountsResponse(BaseModel):
    """Scan counts response."""
    all_count: int
    scan_count: int
    in_count: int
    out_count: int


class CheckResultResponse(BaseModel):
    """Unified scan check result matching frontend LastCheckResult type."""
    status: Literal["allowed", "already_used", "error_invalid", "wrong_event"]
    message: str
    place: str | None = None
    first_check_in: str | None = None
    scanned_by: str | None = None
    reason: str | None = None
    event_name: str | None = None
    event_date: str | None = None
    counts: ScanCountsResponse | None = None


class TicketListItem(BaseModel):
    """Ticket item in list response."""
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


class TicketListResponse(BaseModel):
    """Ticket list response."""
    result: int = 0
    status: str = "success"
    payload: list[TicketListItem] = []


class TicketResponse(BaseModel):
    """Single ticket response."""
    id: int
    serial_number: str | None = None
    price: int
    checked: bool = False
    session_id: int
    title: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class StatisticResponse(BaseModel):
    """Session statistics response."""
    salesAmount: float = 0
    numberOfTickets: int = 0
    numberOfRefundedTickets: int = 0
