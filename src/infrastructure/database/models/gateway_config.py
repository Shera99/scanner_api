from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums.gateway import GatewayTypeEnum
from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.organization import Organization


class GatewayConfig(Base):
    __tablename__ = "gateway_configs"

    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    public_key: Mapped[str] = mapped_column(String(2048), nullable=False)
    private_key: Mapped[str] = mapped_column(String(2048), nullable=False)
    type: Mapped[GatewayTypeEnum] = mapped_column(
        PgEnum(GatewayTypeEnum, name="gatewaytypeenum", create_type=False),
        nullable=False,
    )
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    organization: Mapped["Organization"] = relationship("Organization")
