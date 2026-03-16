from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.scan.check_service import ScanCheckService
from src.application.services.scan.event_service import EventService
from src.application.services.scan.statistic_service import StatisticService
from src.application.services.scan.ticket_service import TicketService
from src.infrastructure.database.repos.scan_log import ScanLogRepository
from src.infrastructure.database.repos.session import SessionRepository
from src.infrastructure.database.repos.ticket import TicketRepository
from src.infrastructure.database.session import get_session


async def get_event_service(session: AsyncSession = Depends(get_session)) -> EventService:
    return EventService(
        session_repo=SessionRepository(session),
        ticket_repo=TicketRepository(session),
    )


async def get_scan_check_service(session: AsyncSession = Depends(get_session)) -> ScanCheckService:
    return ScanCheckService(
        ticket_repo=TicketRepository(session),
        scan_log_repo=ScanLogRepository(session),
        db_session=session,
    )


async def get_ticket_service(session: AsyncSession = Depends(get_session)) -> TicketService:
    return TicketService(
        ticket_repo=TicketRepository(session),
    )


async def get_statistic_service(session: AsyncSession = Depends(get_session)) -> StatisticService:
    return StatisticService(
        ticket_repo=TicketRepository(session),
    )
