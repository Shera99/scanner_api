"""Domain entities package."""
from src.core.entities.enums import (
    ScanType,
    TicketScanStatus,
    UserRole,
    OrderStatus,
    SCAN_TYPE_VALUES,
    SCAN_ALLOWED_ROLES,
    SCAN_ALLOWED_MESSAGES,
    SCAN_ALREADY_USED_MESSAGES,
)

__all__ = [
    "ScanType",
    "TicketScanStatus",
    "UserRole",
    "OrderStatus",
    "SCAN_TYPE_VALUES",
    "SCAN_ALLOWED_ROLES",
    "SCAN_ALLOWED_MESSAGES",
    "SCAN_ALREADY_USED_MESSAGES",
]
