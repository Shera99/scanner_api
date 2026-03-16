from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from src.application.repositories.base import IBaseRepository

if TYPE_CHECKING:
    from src.infrastructure.database.models.session import Session
    from src.infrastructure.database.models.user import UserPermission


class AbstractSessionRepository(IBaseRepository["Session"], ABC):

    @abstractmethod
    async def get_sessions_for_permission(
        self,
        permission: "UserPermission",
        start_time: datetime,
        end_time: datetime,
    ) -> List["Session"]:
        raise NotImplementedError

    @abstractmethod
    async def get_session_by_id(self, session_id: int) -> Optional["Session"]:
        raise NotImplementedError
