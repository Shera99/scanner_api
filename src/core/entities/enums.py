"""Domain enums."""
from enum import Enum


class ScanType(str, Enum):
    """Scan type enumeration."""
    entry = "entry"
    exit = "exit"


class TicketScanStatus(str, Enum):
    """Ticket scan status."""
    scanned = "scanned"
    not_scanned = "notScanned"


SCAN_TYPE_VALUES = {
    ScanType.exit: 0,
    ScanType.entry: 1,
}

SCAN_ALLOWED_MESSAGES = {1: "ПРОХОД РАЗРЕШЁН", 0: "ВЫХОД РАЗРЕШЁН"}

SCAN_ALREADY_USED_MESSAGES = {1: "УЖЕ ИСПОЛЬЗОВАН", 0: "УЖЕ ВЫШЛИ"}


class UserRole(str, Enum):
    """User permission roles."""
    super_admin = "SUPER_ADMIN"
    admin = "ADMIN"
    manager = "MANAGER"
    accountant = "ACCOUNTANT"
    organizer = "ORGANIZER"
    cashier = "CASHIER"
    controller = "CONTROLLER"
    partner = "PARTNER"
    super_cashier = "SUPER_CASHIER"
    artist = "ARTIST"


SCAN_ALLOWED_ROLES = [
    UserRole.controller,
    UserRole.super_admin,
    UserRole.admin,
    UserRole.manager,
]


class OrderStatus(str, Enum):
    """Order status enumeration."""
    booked = "BOOKED"
    sales_booked = "SALES_BOOKED"
    pending_for_payment = "PENDING_FOR_PAYMENT"
    completed = "COMPLETED"
    failed = "FAILED"
    refund = "REFUND"
    cancelled = "CANCELLED"
    invitation = "INVITATION"
