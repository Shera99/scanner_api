"""DTO schemas package."""
from src.application.schemas.dto.user import UserDTO, PermissionDTO
from src.application.schemas.dto.event import EventDTO, SessionDTO
from src.application.schemas.dto.ticket import TicketDTO, TicketListItemDTO
from src.application.schemas.dto.scan import ScanCheckDTO, ScanCountsDTO, StatisticDTO

__all__ = [
    "UserDTO",
    "PermissionDTO",
    "EventDTO",
    "SessionDTO",
    "TicketDTO",
    "TicketListItemDTO",
    "ScanCheckDTO",
    "ScanCountsDTO",
    "StatisticDTO",
]
