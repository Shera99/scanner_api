"""Scan DTOs."""
from datetime import datetime

from pydantic import BaseModel

from src.core.entities import ScanType
from src.core.enums.scan import ScanTypeEnum


class ScanCheckDTO(BaseModel):
    """DTO for scan check operation."""
    session_id: int
    ticket_number: str
    scan_type: ScanType
    code: str | None = None


class ScanCountsDTO(BaseModel):
    """DTO for scan counts."""
    all_count: int
    scan_count: int
    in_count: int
    out_count: int


class StatisticDTO(BaseModel):
    """DTO for session statistics."""
    sales_amount: float = 0
    number_of_tickets: int = 0
    number_of_refunded_tickets: int = 0


class ScanLogEntryDTO(BaseModel):
    """Scan log row for ticket list (joined with user)."""
    date_scan: datetime
    type_scan: ScanTypeEnum
    full_name: str | None = None
