from typing import Optional

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class TicketType(Base):
    __tablename__ = "ticket_types"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(55), nullable=False)

    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ky: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_uz: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    @property
    def title(self) -> str | None:
        return self.title_ru
