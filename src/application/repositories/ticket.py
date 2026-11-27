from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from src.application.repositories.base import IBaseRepository
from src.core.entities.zone import ScanZone

if TYPE_CHECKING:
    from src.infrastructure.database.models.order import OrderItem


class AbstractTicketRepository(IBaseRepository["OrderItem"], ABC):

    @abstractmethod
    async def get_ticket_by_session_and_serial(
        self,
        session_id: int,
        serial_number: str,
    ) -> Optional["OrderItem"]:
        raise NotImplementedError

    @abstractmethod
    async def get_ticket_by_serial(
        self,
        serial_number: str,
    ) -> Optional["OrderItem"]:
        raise NotImplementedError

    @abstractmethod
    async def get_ticket_for_check(
        self,
        serial_number: str,
    ) -> Optional["OrderItem"]:
        """Билет для проверки на входе: только поля, нужные сканеру."""
        raise NotImplementedError

    @abstractmethod
    async def search_tickets_by_email(
        self,
        session_id: int,
        email: str,
    ) -> List["OrderItem"]:
        raise NotImplementedError

    @abstractmethod
    async def get_tickets_for_session(
        self,
        session_id: int,
        last_ticket_id: int = 0,
        scan_status: Optional[bool] = None,
        email_filter: Optional[str] = None,
        limit: int = 50,
    ) -> List["OrderItem"]:
        raise NotImplementedError

    @abstractmethod
    async def get_session_statistics(self, session_id: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_ticket_counts(self, session_id: int, zone: ScanZone | None = None) -> dict:
        """Счётчики сеанса; с зоной — только по билетам этой зоны."""
        raise NotImplementedError

    @abstractmethod
    async def get_ticket_counts_batch(self, session_ids: List[int]) -> dict[int, dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_zone_breakdown(self, session_id: int) -> dict:
        """Из чего можно собрать зону на сеансе: типы билетов, области схемы,
        секторы и проданные билеты в разбивке по ним."""
        raise NotImplementedError

    @abstractmethod
    async def mark_ticket_scanned(
        self,
        ticket_id: int,
        in_out: int,
        updated_at: datetime,
    ) -> bool:
        """Гасит билет одним запросом. False — билет уже отмечен этим же типом
        скана (его успел провести другой сканер)."""
        raise NotImplementedError
