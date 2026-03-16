from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.country import Country


class Region(Base):
    __tablename__ = "regions"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id"), nullable=False)

    country: Mapped["Country"] = relationship("Country")
