from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums.scan import ScanTypeEnum
from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.user import User
    from src.infrastructure.database.models.order import OrderItem


class ScanLog(Base):
    __tablename__ = "scan_logs"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    order_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("order_items.id"), nullable=False)
    date_scan: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    type_scan: Mapped[ScanTypeEnum] = mapped_column(
        PgEnum(ScanTypeEnum, name="scantypeenum", create_type=False),
        default=ScanTypeEnum.in_,
        server_default="IN",
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    order_item: Mapped["OrderItem"] = relationship("OrderItem", foreign_keys=[order_item_id])
