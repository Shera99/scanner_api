from __future__ import annotations

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_json import mutable_json_type

from src.core.enums.session import SessionStatusEnum, SvgTypeEnum
from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.event import Event
    from src.infrastructure.database.models.order import OrderItem


class Session(Base):
    __tablename__ = "sessions"

    slug_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    language: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), nullable=False)
    hall_id: Mapped[int] = mapped_column(Integer, ForeignKey("halls.id"), nullable=False)
    scheme_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("schemes.id"), nullable=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_informational: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    status: Mapped[SessionStatusEnum] = mapped_column(
        PgEnum(SessionStatusEnum, name="sessionstatusenum", create_type=False),
        default=SessionStatusEnum.active,
        server_default=SessionStatusEnum.active.value,
    )
    max_tickets_per_customer: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    turnstile_data: Mapped[Optional[dict]] = mapped_column(
        mutable_json_type(dbtype=JSONB, nested=True), nullable=True
    )
    is_cancelled_session: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, server_default="false", nullable=True)

    outer_session_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    svg_type: Mapped[Optional[SvgTypeEnum]] = mapped_column(
        PgEnum(SvgTypeEnum, name="svgtypeenum", create_type=False),
        default=SvgTypeEnum.our_system,
        nullable=True,
    )

    event: Mapped["Event"] = relationship("Event", back_populates="sessions")
    hall: Mapped["Hall"] = relationship("Hall")
    scheme: Mapped[Optional["Scheme"]] = relationship("Scheme")

    ticket_types: Mapped[List["TicketType"]] = relationship("TicketType")
    areas: Mapped[List["TicketArea"]] = relationship("TicketArea")
    seats: Mapped[List["TicketSeat"]] = relationship("TicketSeat")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="session")

    @property
    def slug(self) -> str | None:
        return self.slug_ru
