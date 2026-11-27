from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, case, or_, and_, update, table, column, true, false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.attributes import set_committed_value

from src.application.repositories.ticket import AbstractTicketRepository
from src.core.entities.zone import ScanZone
from src.infrastructure.database.features import db_features
from src.infrastructure.database.models.order import OrderItem, Order
from src.infrastructure.database.models.scheme_area import SchemeArea
from src.infrastructure.database.models.session import Session
from src.infrastructure.database.models.event import Event
from src.core.enums.order import OrderStatusEnum
from src.infrastructure.database.models.ticket_area import TicketArea
from src.infrastructure.database.models.ticket_seat import TicketSeat
from src.infrastructure.database.models.ticket_type import TicketType
from src.infrastructure.database.models.user import User
from src.infrastructure.database.repos.base import BaseRepository


_TICKET_EAGER_OPTIONS = [
    joinedload(OrderItem.order).joinedload(Order.user),
    joinedload(OrderItem.ticket_type),
    joinedload(OrderItem.session).joinedload(Session.event),
]

# Доп. опции сеанса. Не модель: сервис при старте создаёт недостающие таблицы
# своих моделей, а эту ведёт showgo_api, и в базах части стран её нет.
_session_options = table("session_options", column("id"), column("session_id"), column("title"))


def _check_loaders() -> list:
    # Что читать из базы при проверке на входе — одинаково для билета и для
    # доп. опции, проверяются они одним путём. Нужны несколько полей: целые
    # строки заказа, покупателя и мероприятия (описания, JSON) на каждый скан
    # не читаем.
    columns = [
        OrderItem.serial_number,
        OrderItem.title_ru,
        OrderItem.session_id,
        OrderItem.order_id,
        OrderItem.is_refund,
        OrderItem.checked,
        OrderItem.in_out,
        OrderItem.ticket_type_id,
        OrderItem.ticket_area_id,
        OrderItem.ticket_seat_id,
    ]
    if db_features.session_options:
        columns.append(OrderItem.session_option_id)
    return [
        load_only(*columns),
        joinedload(OrderItem.order).load_only(Order.status),
        joinedload(OrderItem.session)
        .load_only(Session.date_time)
        .joinedload(Session.event)
        .load_only(Event.title_ru),
        joinedload(OrderItem.ticket_seat).load_only(TicketSeat.sector),
    ]


_VALID_STATUSES = [OrderStatusEnum.completed, OrderStatusEnum.invitation]

# Место без сектора — сектор с пустым названием (как в ScanZone.allows).
_SECTOR = func.coalesce(func.btrim(TicketSeat.sector), "")


def _tickets_only():
    """Доп. опции сеанса — не билеты: в счётчики билетов не входят."""
    return OrderItem.session_option_id.is_(None) if db_features.session_options else true()


def _zone_condition(session_id: int, zone: ScanZone):
    """SQL-условие «билет входит в зону». Правила те же, что в ScanZone.allows."""
    rules = []
    if zone.all_seats:
        rules.append(OrderItem.ticket_seat_id.is_not(None))
    elif zone.sectors:
        rules.append(OrderItem.ticket_seat_id.in_(
            select(TicketSeat.id).where(
                TicketSeat.session_id == session_id,
                _SECTOR.in_(zone.sectors),
            )
        ))
    if zone.all_entry:
        rules.append(and_(OrderItem.ticket_seat_id.is_(None), _tickets_only()))
    if zone.type_ids:
        rules.append(OrderItem.ticket_type_id.in_(zone.type_ids))
    if zone.area_ids:
        rules.append(OrderItem.ticket_area_id.in_(zone.area_ids))
    if zone.option_ids and db_features.session_options:
        rules.append(OrderItem.session_option_id.in_(zone.option_ids))
    return or_(*rules) if rules else false()


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

    async def get_ticket_for_check(
        self,
        serial_number: str,
    ) -> Optional[OrderItem]:
        result = await self.session.execute(
            select(OrderItem)
            .where(OrderItem.serial_number == serial_number)
            .options(*_check_loaders())
        )
        ticket = result.unique().scalars().first()
        if ticket is not None and not db_features.session_options:
            # колонки в базе нет: опций не бывает, а обращение к полю не должно идти в базу
            set_committed_value(ticket, "session_option_id", None)
        return ticket

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

    async def get_ticket_counts(self, session_id: int, zone: ScanZone | None = None) -> dict:
        query = (
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
                Order.status.in_(_VALID_STATUSES),
                OrderItem.is_refund.is_(False),
            )
        )
        if zone is not None and zone.has_rules:
            query = query.where(_zone_condition(session_id, zone))
        else:
            query = query.where(_tickets_only())

        result = await self.session.execute(query)
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
                Order.status.in_(_VALID_STATUSES),
                OrderItem.is_refund.is_(False),
                _tickets_only(),
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

    async def get_zone_breakdown(self, session_id: int) -> dict:
        seated = OrderItem.ticket_seat_id.is_not(None)
        groups = [OrderItem.ticket_type_id, OrderItem.ticket_area_id, seated, _SECTOR]
        columns = [OrderItem.ticket_type_id, OrderItem.ticket_area_id, seated.label("seated"), _SECTOR.label("sector")]
        if db_features.session_options:
            groups.append(OrderItem.session_option_id)
            columns.append(OrderItem.session_option_id)

        sold = await self.session.execute(
            select(
                *columns,
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
            .outerjoin(TicketSeat, OrderItem.ticket_seat_id == TicketSeat.id)
            .where(
                OrderItem.session_id == session_id,
                Order.status.in_(_VALID_STATUSES),
                OrderItem.is_refund.is_(False),
            )
            .group_by(*groups)
        )
        types = await self.session.execute(
            select(TicketType.id, TicketType.title_ru)
            .where(TicketType.session_id == session_id)
            .order_by(TicketType.id)
        )
        areas = await self.session.execute(
            select(TicketArea.id, SchemeArea.title_ru)
            .join(SchemeArea, TicketArea.scheme_area_id == SchemeArea.id)
            .where(TicketArea.session_id == session_id)
            .order_by(TicketArea.id)
        )
        sectors = await self.session.execute(
            select(_SECTOR)
            .where(TicketSeat.session_id == session_id)
            .distinct()
        )
        options = []
        if db_features.session_options:
            result = await self.session.execute(
                select(_session_options.c.id, _session_options.c.title.label("title_ru"))
                .where(_session_options.c.session_id == session_id)
                .order_by(_session_options.c.id)
            )
            options = [dict(row) for row in result.mappings().all()]

        return {
            "sold": [dict(row) for row in sold.mappings().all()],
            "types": [dict(row) for row in types.mappings().all()],
            "areas": [dict(row) for row in areas.mappings().all()],
            "sectors": list(sectors.scalars().all()),
            "options": options,
        }

    async def mark_ticket_scanned(
        self,
        ticket_id: int,
        in_out: int,
        updated_at: datetime,
    ) -> bool:
        # Условие в самом UPDATE: если два сканера провели один билет одновременно,
        # строку изменит только первый, второй получит 0 строк.
        result = await self.session.execute(
            update(OrderItem)
            .where(
                OrderItem.id == ticket_id,
                or_(
                    OrderItem.checked.is_not(True),
                    OrderItem.in_out.is_distinct_from(in_out),
                ),
            )
            .values(checked=True, in_out=in_out, updated_at=updated_at)
            .execution_options(synchronize_session=False)
        )
        return result.rowcount > 0
