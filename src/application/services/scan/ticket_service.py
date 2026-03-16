from src.application.repositories.ticket import AbstractTicketRepository
from src.application.schemas.response import (
    TicketListItem,
    TicketListResponse,
    TicketResponse,
)
from src.application.services.crypto import TicketCryptographyService
from src.core.exceptions import NotFoundException


class TicketService:

    def __init__(self, ticket_repo: AbstractTicketRepository):
        self.ticket_repo = ticket_repo
        self.crypto_service = TicketCryptographyService()

    async def get_ticket_list(
        self,
        session_id: int,
        last_ticket_id: int = 0,
        scan_status: str | None = None,
        email_filter: str | None = None,
    ) -> TicketListResponse:
        status_map = {"scanned": True, "notScanned": False}
        checked_filter = status_map.get(scan_status) if scan_status else None

        tickets = await self.ticket_repo.get_tickets_for_session(
            session_id=session_id,
            last_ticket_id=last_ticket_id,
            scan_status=checked_filter,
            email_filter=email_filter,
            limit=50,
        )

        result = []
        for ticket in tickets:
            ticket_type_name = None
            if ticket.ticket_type:
                ticket_type_name = getattr(ticket.ticket_type, "title_ru", None)

            qr_number = self.crypto_service.encrypt(ticket.serial_number) if ticket.serial_number else None

            item = TicketListItem(
                id=ticket.id,
                serial_number=ticket.serial_number,
                checked=ticket.checked,
                order_status=ticket.order.status.value if ticket.order and ticket.order.status else None,
                ticket_type=ticket_type_name,
                place=ticket.title,
                price=ticket.price,
                qr_number=qr_number,
                user_name=ticket.order.user.full_name if ticket.order and ticket.order.user else None,
                user_email=ticket.order.user.email if ticket.order and ticket.order.user else None,
                user_phone=ticket.order.user.phone_number if ticket.order and ticket.order.user else None,
                order_date=ticket.created_at,
            )
            result.append(item)

        return TicketListResponse(result=0, status="success", payload=result)

    async def search_tickets_by_email(
        self,
        session_id: int,
        email: str,
    ) -> TicketListResponse:
        tickets = await self.ticket_repo.search_tickets_by_email(
            session_id=session_id,
            email=email,
        )

        result = []
        for ticket in tickets:
            ticket_type_name = None
            if ticket.ticket_type:
                ticket_type_name = getattr(ticket.ticket_type, "title_ru", None)

            qr_number = self.crypto_service.encrypt(ticket.serial_number) if ticket.serial_number else None

            item = TicketListItem(
                id=ticket.id,
                serial_number=ticket.serial_number,
                checked=ticket.checked,
                order_status=ticket.order.status.value if ticket.order and ticket.order.status else None,
                ticket_type=ticket_type_name,
                place=ticket.title,
                price=ticket.price,
                qr_number=qr_number,
                user_name=ticket.order.user.full_name if ticket.order and ticket.order.user else None,
                user_email=ticket.order.user.email if ticket.order and ticket.order.user else None,
                user_phone=ticket.order.user.phone_number if ticket.order and ticket.order.user else None,
                order_date=ticket.created_at,
            )
            result.append(item)

        return TicketListResponse(result=0, status="success", payload=result)

    async def search_ticket(
        self,
        session_id: int,
        ticket_number: str,
    ) -> TicketResponse:
        ticket = await self.ticket_repo.get_ticket_by_session_and_serial(
            session_id=session_id,
            serial_number=ticket_number,
        )

        if not ticket:
            raise NotFoundException("Билет не найден!")

        return TicketResponse(
            id=ticket.id,
            serial_number=ticket.serial_number,
            price=ticket.price,
            checked=ticket.checked,
            session_id=ticket.session_id,
            title=ticket.title,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )
