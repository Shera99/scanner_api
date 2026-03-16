from __future__ import annotations

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_json import mutable_json_type

from src.core.enums.order import OrderStatusEnum, PaymentMethodEnum
from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.user import User
    from src.infrastructure.database.models.session import Session


class Order(Base):
    __tablename__ = "orders"

    order_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    discount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timer: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[OrderStatusEnum] = mapped_column(
        PgEnum(OrderStatusEnum, name="orderstatusenum", create_type=False),
        default=OrderStatusEnum.booked,
    )
    payload: Mapped[Optional[dict]] = mapped_column(
        mutable_json_type(dbtype=JSONB, nested=True), nullable=True
    )
    analytics: Mapped[Optional[dict]] = mapped_column(
        mutable_json_type(dbtype=JSONB, nested=True), nullable=True
    )

    cashier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    gateway_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("gateway_configs.id"), nullable=True)

    payment_method: Mapped[PaymentMethodEnum] = mapped_column(
        PgEnum(PaymentMethodEnum, name="paymentmethodenum", create_type=False),
        default=PaymentMethodEnum.cash,
    )

    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_partner_sale: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    invitation_comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    was_invitation: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    order_comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    booked_comment: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    total_service_fee: Mapped[Optional[int]] = mapped_column(Integer, default=0, server_default="0", nullable=True)

    is_esbo: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, server_default="false", nullable=True)
    esbo_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    agent_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    cashier: Mapped[Optional["User"]] = relationship("User", foreign_keys=[cashier_id])
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", foreign_keys="OrderItem.order_id")


class OrderItem(Base):
    __tablename__ = "order_items"

    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    order_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("orders.id"), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    discount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ticket_area_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ticket_areas.id"), nullable=True)
    ticket_type_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ticket_types.id"), nullable=True)
    ticket_seat_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ticket_seats.id"), nullable=True)
    # ticket_theater_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("theater_tickets.id"), nullable=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False)
    html_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_refund: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    checked: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    in_out: Mapped[int] = mapped_column(Integer, default=0)
    counter: Mapped[Optional[dict]] = mapped_column(
        mutable_json_type(dbtype=JSONB, nested=True),
        nullable=True,
        default={"is_mailed": False, "count_mailed": 0, "count_installed": 0, "count_printed": 0},
    )
    hide_price: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    service_fee: Mapped[Optional[int]] = mapped_column(Integer, default=0, server_default="0", nullable=True)
    is_sold: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, server_default="false", nullable=True)

    turnstile_or_other_data: Mapped[Optional[dict]] = mapped_column(
        mutable_json_type(dbtype=JSONB, nested=True), nullable=True
    )
    turnstile_qr_ticket_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("turnstile_qr_tickets.id"), nullable=True
    )

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    session: Mapped["Session"] = relationship("Session", back_populates="order_items")
    ticket_type: Mapped[Optional["TicketType"]] = relationship("TicketType")

    @property
    def title(self) -> str | None:
        return self.title_ru
