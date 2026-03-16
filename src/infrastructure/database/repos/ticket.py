from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, case, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.repositories.ticket import AbstractTicketRepository
from src.infrastructure.database.models.order import OrderItem, Order
from src.infrastructure.database.models.session import Session
from src.infrastructure.database.models.event import Event
from src.core.enums.order import OrderStatusEnum
from src.infrastructure.database.models.user import User
from src.infrastructure.database.repos.base import BaseRepository


_TICKET_EAGER_OPTIONS = [
    joinedload(OrderItem.order).joinedload(Order.user),
    joinedload(OrderItem.ticket_type),
    joinedload(OrderItem.session).joinedload(Session.event),
]


class TicketRepository(BaseRepository[OrderItem], AbstractTicketRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, OrderItem)

    async def get_ticket_by_session_and_serial(
        self,
        session_id: int,
        serial_number: str,
    ) -> Optional[OrderItem]:
        result = await self.session.execute(
            select(OrderItem)
            .where(
                OrderItem.session_id == session_id,
                OrderItem.serial_number == serial_number,
            )
            .options(*_TICKET_EAGER_OPTIONS)
        )
        return result.unique().scalars().first()

    async def get_ticket_by_serial(
        self,
        serial_number: str,
    ) -> Optional[OrderItem]:
        result = await self.session.execute(
            select(OrderItem)
            .where(OrderItem.serial_number == serial_number)
            .options(*_TICKET_EAGER_OPTIONS)
        )
        return result.unique().scalars().first()

    async def search_tickets_by_email(
        self,
        session_id: int,
        email: str,
    ) -> List[OrderItem]:
        result = await self.session.execute(
            select(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .join(User, Order.user_id == User.id)
            .where(
                OrderItem.session_id == session_id,
                Order.status == OrderStatusEnum.completed,
                User.email.ilike(f"%{email}%"),
            )
            .options(*_TICKET_EAGER_OPTIONS)
            .order_by(OrderItem.id)
        )
        return list(result.unique().scalars().all())

    async def get_tickets_for_session(
        self,
        session_id: int,
        last_ticket_id: int = 0,
        scan_status: Optional[bool] = None,
        email_filter: Optional[str] = None,
        limit: int = 50,
    ) -> List[OrderItem]:
        query = (
            select(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .join(User, Order.user_id == User.id)
            .where(
                OrderItem.session_id == session_id,
                Order.status == OrderStatusEnum.completed,
            )
            .options(*_TICKET_EAGER_OPTIONS)
        )

        if last_ticket_id > 0:
            query = query.where(OrderItem.id > last_ticket_id)

        if email_filter:
            query = query.where(User.email.like(f"%{email_filter}%"))

        if scan_status is not None:
            query = query.where(OrderItem.checked == scan_status)

        query = query.order_by(OrderItem.id).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def get_session_statistics(self, session_id: int) -> dict:
        valid_statuses = [OrderStatusEnum.completed, OrderStatusEnum.invitation]
        refund_statuses = [OrderStatusEnum.refund, OrderStatusEnum.cancelled]

        result = await self.session.execute(
            select(
                func.sum(
                    case(
                        (
                            (Order.status == OrderStatusEnum.completed) & (OrderItem.is_refund.is_(False)),
                            OrderItem.price,
                        ),
                        else_=0,
                    )
                ).label("sales_amount"),
                func.count().filter(
                    Order.status.in_(valid_statuses),
                    OrderItem.is_refund.is_(False),
                ).label("number_of_tickets"),
                func.count().filter(
                    or_(
                        Order.status.in_(refund_statuses),
                        OrderItem.is_refund.is_(True),
                    )
                ).label("number_of_refunded_tickets"),
            )
            .join(Order)
            .where(OrderItem.session_id == session_id)
        )
        row = result.first()

        return {
            "sales_amount": row.sales_amount or 0,
            "number_of_tickets": row.number_of_tickets or 0,
            "number_of_refunded_tickets": row.number_of_refunded_tickets or 0,
        }

    async def get_ticket_counts(self, session_id: int) -> dict:
        valid_statuses = [OrderStatusEnum.completed, OrderStatusEnum.invitation]

        result = await self.session.execute(
            select(
                func.count().label("all_count"),
                func.count().filter(OrderItem.checked.is_(True)).label("scan_count"),
                func.count().filter(
                    OrderItem.checked.is_(True), OrderItem.in_out == 1
                ).label("in_count"),
                func.count().filter(
                    OrderItem.checked.is_(True), OrderItem.in_out == 0
                ).label("out_count"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                OrderItem.session_id == session_id,
                Order.status.in_(valid_statuses),
                OrderItem.is_refund.is_(False),
            )
        )
        row = result.first()
        return {
            "all_count": row.all_count or 0,
            "scan_count": row.scan_count or 0,
            "in_count": row.in_count or 0,
            "out_count": row.out_count or 0,
        }

    async def get_ticket_counts_batch(self, session_ids: List[int]) -> dict[int, dict]:
        if not session_ids:
            return {}

        valid_statuses = [OrderStatusEnum.completed, OrderStatusEnum.invitation]

        result = await self.session.execute(
            select(
                OrderItem.session_id,
                func.count().label("all_count"),
                func.count().filter(OrderItem.checked.is_(True)).label("scan_count"),
                func.count().filter(
                    OrderItem.checked.is_(True), OrderItem.in_out == 1
                ).label("in_count"),
                func.count().filter(
                    OrderItem.checked.is_(True), OrderItem.in_out == 0
                ).label("out_count"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                OrderItem.session_id.in_(session_ids),
                Order.status.in_(valid_statuses),
                OrderItem.is_refund.is_(False),
            )
            .group_by(OrderItem.session_id)
        )

        counts: dict[int, dict] = {}
        for row in result.all():
            counts[row.session_id] = {
                "all_count": row.all_count or 0,
                "scan_count": row.scan_count or 0,
                "in_count": row.in_count or 0,
                "out_count": row.out_count or 0,
            }
        return counts

    async def update_ticket_scan(
        self,
        ticket: OrderItem,
        checked: bool,
        in_out: int,
        updated_at: datetime,
    ) -> OrderItem:
        ticket.checked = checked
        ticket.in_out = in_out
        ticket.updated_at = updated_at
        self.session.add(ticket)
        await self.session.flush()
        return ticket
