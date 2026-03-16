from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class Country(Base):
    __tablename__ = "countries"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    currency_prefix: Mapped[Optional[str]] = mapped_column(String(55), nullable=True)
    currency_suffix: Mapped[Optional[str]] = mapped_column(String(55), nullable=True)
    code: Mapped[str] = mapped_column(String(55), nullable=False, server_default="kg")
    time_zone_difference: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    @property
    def title(self) -> str | None:
        return self.title_ru
