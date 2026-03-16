from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Float, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums.organization import ServiceFeeTypeEnum, OrganizationTypeEnum
from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.address import Address


class Organization(Base):
    __tablename__ = "organizations"

    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ky: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_kz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_tj: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    inn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(55), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    address_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("addresses.id"), nullable=True)
    bank_details: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telegram_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    whatsapp_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    okpo: Mapped[Optional[str]] = mapped_column(String(355), nullable=True)
    bik: Mapped[Optional[str]] = mapped_column(String(355), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(355), nullable=True)
    bank_account: Mapped[Optional[str]] = mapped_column(String(355), nullable=True)
    vat: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    commission: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    taxe_is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_enabled_showing_logo: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_enabled_offline_fiscal: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    service_fee_value: Mapped[float] = mapped_column(Float, nullable=True, default=0.0, server_default="0.0")

    type = mapped_column(
        PgEnum(OrganizationTypeEnum, name="organizationtypeenum", create_type=False),
        nullable=True,
    )
    service_fee_type = mapped_column(
        PgEnum(ServiceFeeTypeEnum, name="servicefeetypeenum", create_type=False),
        default=ServiceFeeTypeEnum.fixed,
        server_default="fixed",
    )

    address: Mapped[Optional["Address"]] = relationship("Address")

    @property
    def title(self) -> str | None:
        return self.title_ru
