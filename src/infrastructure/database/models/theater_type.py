from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class TheaterType(Base):
    __tablename__ = "theater_types"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_tj: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_kz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
