"""Request schemas package."""
from src.application.schemas.request.auth import AuthRequest
from src.application.schemas.request.scan import (
    ScanCheckData,
    ScanCheckRequest,
    TicketListQuery,
    TicketSearchRequest,
    TicketSearchByMailRequest,
)

__all__ = [
    "AuthRequest",
    "ScanCheckData",
    "ScanCheckRequest",
    "TicketListQuery",
    "TicketSearchRequest",
    "TicketSearchByMailRequest",
]
