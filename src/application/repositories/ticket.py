from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from src.application.repositories.base import IBaseRepository

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
    async def get_ticket_counts(self, session_id: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_ticket_counts_batch(self, session_ids: List[int]) -> dict[int, dict]:
        raise NotImplementedError

    @abstractmethod
    async def update_ticket_scan(
        self,
        ticket: "OrderItem",
        checked: bool,
        in_out: int,
        updated_at: datetime,
    ) -> "OrderItem":
        raise NotImplementedError
