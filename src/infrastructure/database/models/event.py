from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Integer, String, Text, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_json import mutable_json_type

from src.core.enums.event import EventStatusEnum, EventScannerTypeEnum
from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.session import Session


class Event(Base):
    __tablename__ = "events"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_kz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_tj: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ky: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_uz: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_kz: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_tj: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    age_restriction: Mapped[Optional[str]] = mapped_column(String(55), nullable=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_active: Mapped[EventStatusEnum] = mapped_column(
        PgEnum(EventStatusEnum, name="eventstatusenum", create_type=False),
        default=EventStatusEnum.active,
        server_default="ACTIVE",
    )
    duration: Mapped[Optional[int]] = mapped_column(nullable=True)
    image_path: Mapped[str] = mapped_column(String(255))
    youtube_video: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    commission: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    taxe_is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    mail: Mapped[Optional[dict]] = mapped_column(
        mutable_json_type(dbtype=JSONB, nested=True),
        nullable=True,
        default={"title": None, "text": None, "image": None},
    )
    ikpu: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    header_image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    footer_image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ticket_rule: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ticket_logo_is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    ads_image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ads_image_is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    sponsor_logo_image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price_from: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    is_invitations_enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_service_fee_enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_cancelled_event: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, server_default="false", nullable=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_entrances_active: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_fiscalized: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, server_default="false", nullable=True)
    is_daily_scanning_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_qr_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pinned: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, server_default="false", nullable=True)

    scanner_type: Mapped[EventScannerTypeEnum] = mapped_column(
        PgEnum(EventScannerTypeEnum, name="eventscannertypeenum", create_type=False),
        default=EventScannerTypeEnum.scanner,
        server_default="SCANNER",
    )
    turnstile_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    template_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    outer_event_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    theater_id: Mapped[int] = mapped_column(Integer, ForeignKey("theaters.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)

    organization: Mapped["Organization"] = relationship("Organization")
    category: Mapped["Category"] = relationship("Category")
    theater: Mapped["Theater"] = relationship("Theater")
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="event")

    @property
    def title(self) -> str | None:
        return self.title_ru

    @property
    def description(self) -> str | None:
        return self.description_ru
