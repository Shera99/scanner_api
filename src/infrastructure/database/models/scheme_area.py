from typing import Optional

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class SchemeArea(Base):
    __tablename__ = "scheme_areas"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey("schemes.id"), nullable=False)
