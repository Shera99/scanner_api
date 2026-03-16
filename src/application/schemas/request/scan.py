"""Scan request schemas."""
from pydantic import BaseModel, EmailStr, Field

from src.core.entities import ScanType


class ScanCheckData(BaseModel):
    """Inner data for scan check request."""
    session_id: int = Field(..., description="Session ID")
    type: ScanType = Field(..., description="Scan type: entry or exit")
    code: str | None = Field(None, description="Encrypted ticket code (QR)")
    no_code: str | None = Field(None, description="Plain ticket number")


class ScanCheckRequest(BaseModel):
    """Scan check request schema."""
    data: ScanCheckData = Field(..., description="Scan check data")


class TicketListQuery(BaseModel):
    """Query parameters for ticket list."""
    type: str | None = Field(None, description="Filter by scan status: scanned or notScanned")
    email: str | None = Field(None, description="Filter by user email")


class TicketSearchRequest(BaseModel):
    """Ticket search by number request."""
    session_id: int = Field(..., description="Session ID")
    ticket_number: str = Field(..., description="Ticket serial number")


class TicketSearchByMailRequest(BaseModel):
    """Ticket search by email request."""
    session_id: int = Field(..., description="Session ID")
    email: EmailStr = Field(..., description="User email")
