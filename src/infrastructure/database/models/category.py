from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class Category(Base):
    __tablename__ = "categories"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    @property
    def title(self) -> str | None:
        return self.title_ru
