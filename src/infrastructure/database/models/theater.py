from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.address import Address
    from src.infrastructure.database.models.region import Region
    from src.infrastructure.database.models.theater_type import TheaterType


class Theater(Base):
    __tablename__ = "theaters"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_tj: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_kz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("regions.id"), nullable=False)
    theater_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("theater_types.id"), nullable=False)
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey("addresses.id"), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, server_default="true", nullable=True)

    region: Mapped["Region"] = relationship("Region")
    address: Mapped["Address"] = relationship("Address")
    theater_type: Mapped["TheaterType"] = relationship("TheaterType")

    @property
    def title(self) -> str | None:
        return self.title_ru
