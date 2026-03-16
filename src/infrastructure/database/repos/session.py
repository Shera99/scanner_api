import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.repositories.session import AbstractSessionRepository
from src.application.repositories.user import FULL_ACCESS_ROLES
from src.infrastructure.database.models.event import Event
from src.infrastructure.database.models.region import Region
from src.infrastructure.database.models.session import Session
from src.infrastructure.database.models.theater import Theater
from src.infrastructure.database.models.user import UserPermission
from src.infrastructure.database.repos.base import BaseRepository

logger = logging.getLogger(__name__)

_SESSION_EAGER_OPTIONS = [
    joinedload(Session.event).joinedload(Event.category),
    joinedload(Session.event).joinedload(Event.theater).joinedload(Theater.address),
]


class SessionRepository(BaseRepository[Session], AbstractSessionRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Session)

    async def get_sessions_for_permission(
        self,
        permission: UserPermission,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Session]:
        always_visible = Event.is_daily_scanning_enabled == True
        date_filter = (Session.date_time >= start_time) & (Session.date_time <= end_time)

        if permission.role in FULL_ACCESS_ROLES:
            scope_filter = date_filter
        elif permission.event_id is not None:
            scope_filter = date_filter & (Session.event_id == permission.event_id)
        elif permission.organization_id is not None:
            scope_filter = date_filter & (Event.organization_id == permission.organization_id)
        elif permission.theater_id is not None:
            scope_filter = date_filter & (Event.theater_id == permission.theater_id)
        elif permission.country_id is not None:
            scope_filter = date_filter & (Region.country_id == permission.country_id)
        else:
            scope_filter = None

        if scope_filter is None:
            query = (
                select(Session)
                .join(Event)
                .where(always_visible)
                .options(*_SESSION_EAGER_OPTIONS)
            )
        else:
            query = (
                select(Session)
                .join(Event)
                .outerjoin(Theater, Event.theater_id == Theater.id)
                .outerjoin(Region, Theater.region_id == Region.id)
                .where(or_(always_visible, scope_filter))
                .options(*_SESSION_EAGER_OPTIONS)
            )

        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_session_by_id(self, session_id: int) -> Optional[Session]:
        result = await self.session.execute(
            select(Session)
            .where(Session.id == session_id)
            .options(*_SESSION_EAGER_OPTIONS)
        )
        return result.unique().scalars().first()
