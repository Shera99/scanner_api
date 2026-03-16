from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class TurnstileQrTicket(Base):
    __tablename__ = "turnstile_qr_tickets"

    external_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    start_date: Mapped[str] = mapped_column(String, nullable=False)
    end_date: Mapped[str] = mapped_column(String, nullable=False)
    visitor_family_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    visitor_given_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    certificate_no: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    visit_reason_detail: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    appoint_record_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    visitor_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    appoint_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    approval_flow_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    qr_code_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, server_default="true")
