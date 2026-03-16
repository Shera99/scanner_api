from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=text("(timezone('utc', now()))"), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None, nullable=True)
