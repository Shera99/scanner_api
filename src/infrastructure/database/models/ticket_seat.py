from typing import Optional

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class TicketSeat(Base):
    __tablename__ = "ticket_seats"

    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False)
    html_id: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    sector: Mapped[Optional[str]] = mapped_column(String(55), nullable=True)
    row: Mapped[Optional[str]] = mapped_column(String(55), nullable=True)
    seat: Mapped[Optional[str]] = mapped_column(String(55), nullable=True)
    color: Mapped[str] = mapped_column(String(55), nullable=False)
    scheme_sector_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
