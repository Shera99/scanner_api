from datetime import datetime

from src.application.repositories.session import AbstractSessionRepository
from src.application.repositories.ticket import AbstractTicketRepository
from src.application.schemas.response import EventListItem, EventListResponse
from src.infrastructure.database.models.user import UserPermission


class EventService:

    def __init__(
        self,
        session_repo: AbstractSessionRepository,
        ticket_repo: AbstractTicketRepository,
    ):
        self.session_repo = session_repo
        self.ticket_repo = ticket_repo

    async def get_events_for_permission(
        self,
        permission: UserPermission,
    ) -> EventListResponse:
        current_time = datetime.utcnow()
        start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        sessions = await self.session_repo.get_sessions_for_permission(
            permission=permission,
            start_time=start_time,
            end_time=end_time,
        )

        session_ids = [s.id for s in sessions]
        counts_map = await self.ticket_repo.get_ticket_counts_batch(session_ids)

        events = []
        for session in sessions:
            event = session.event
            if not event:
                continue

            counts = counts_map.get(session.id, {})

            event_item = EventListItem(
                id=session.id,
                event_id=event.id,
                event_name=event.title,
                category_id=event.category_id if hasattr(event, "category_id") else None,
                category_name=event.category.title if hasattr(event, "category") and event.category else None,
                image=event.image_path if hasattr(event, "image_path") else None,
                date_time=session.date_time,
                all_count=counts.get("all_count", 0),
                scan_count=counts.get("scan_count", 0),
                theater_name=event.theater.title if hasattr(event, "theater") and event.theater else None,
                address=event.theater.address.title if hasattr(event, "theater") and event.theater and hasattr(event.theater, "address") and event.theater.address else None,
                inCount=counts.get("in_count", 0),
                outCount=counts.get("out_count", 0),
            )
            events.append(event_item)

        return EventListResponse(events=events)
