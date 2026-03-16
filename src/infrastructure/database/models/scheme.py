from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class Scheme(Base):
    __tablename__ = "schemes"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    @property
    def title(self) -> str | None:
        return self.title_ru
