from enum import Enum


class EventStatusEnum(str, Enum):
    active = "ACTIVE"
    completed = "COMPLETED"
    special_active = "SPECIAL_ACTIVE"
    special_completed = "SPECIAL_COMPLETED"
    draft = "DRAFT"
    awaiting_clarification = "AWAITING_CLARIFICATION"
    soon = "SOON"


class EventScannerTypeEnum(str, Enum):
    scanner = "SCANNER"
    turnstile = "TURNSTILE"
