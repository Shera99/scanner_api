from src.application.repositories.ticket import AbstractTicketRepository
from src.application.schemas.response import StatisticResponse


class StatisticService:

    def __init__(self, ticket_repo: AbstractTicketRepository):
        self.ticket_repo = ticket_repo

    async def get_session_statistics(self, session_id: int) -> StatisticResponse:
        stats = await self.ticket_repo.get_session_statistics(session_id)

        return StatisticResponse(
            salesAmount=stats["sales_amount"],
            numberOfTickets=stats["number_of_tickets"],
            numberOfRefundedTickets=stats["number_of_refunded_tickets"],
        )
