from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.theater import Theater


class Hall(Base):
    __tablename__ = "halls"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_tj: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_kz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    theater_id: Mapped[int] = mapped_column(Integer, ForeignKey("theaters.id"), nullable=False)

    theater: Mapped["Theater"] = relationship("Theater")

    @property
    def title(self) -> str | None:
        return self.title_ru
