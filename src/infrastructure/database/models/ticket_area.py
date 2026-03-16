from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.scheme_area import SchemeArea


class TicketArea(Base):
    __tablename__ = "ticket_areas"

    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False)
    scheme_area_id: Mapped[int] = mapped_column(Integer, ForeignKey("scheme_areas.id"), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(55), nullable=False)

    scheme_area: Mapped["SchemeArea"] = relationship("SchemeArea")
