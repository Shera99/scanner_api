from __future__ import annotations

import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums.user import UserPermissionRoleEnum, GenderEnum
from src.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.event import Event
    from src.infrastructure.database.models.session import Session
    from src.infrastructure.database.models.country import Country


class User(Base):
    __tablename__ = "users"

    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    encrypted_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)

    provider_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_uid: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    birthday: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(
        PgEnum(GenderEnum, name="genderenum", create_type=False), nullable=True
    )

    percent: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    country_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("countries.id"), nullable=True)
    firebase_user_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class UserPermission(Base):
    __tablename__ = "user_permissions"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role: Mapped[UserPermissionRoleEnum] = mapped_column(
        PgEnum(UserPermissionRoleEnum, name="userpermissionroleenum", create_type=False),
        nullable=False,
    )

    percent: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)

    event_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("events.id"), nullable=True)
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=True)
    country_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("countries.id"), nullable=True)
    theater_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("theaters.id"), nullable=True)

    event: Mapped[Optional["Event"]] = relationship("Event", foreign_keys=[event_id])
    session: Mapped[Optional["Session"]] = relationship("Session", foreign_keys=[session_id])
    organization: Mapped[Optional["Organization"]] = relationship("Organization", foreign_keys=[organization_id])
    country: Mapped[Optional["Country"]] = relationship("Country", foreign_keys=[country_id])
    theater: Mapped[Optional["Theater"]] = relationship("Theater", foreign_keys=[theater_id])
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    by_country: Mapped[bool] = mapped_column(Boolean, default=False)
    by_accountant_all: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_invitations_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    weekly_sales_amount: Mapped[float] = mapped_column(Float, default=0.0)

    @property
    def is_partner(self) -> bool:
        return self.role == UserPermissionRoleEnum.partner

    @property
    def is_accountant(self) -> bool:
        return self.role == UserPermissionRoleEnum.accountant

    @property
    def is_manager(self) -> bool:
        return self.role == UserPermissionRoleEnum.manager

    @property
    def is_admin(self) -> bool:
        return self.role == UserPermissionRoleEnum.admin

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserPermissionRoleEnum.super_admin

    @property
    def is_organizer(self) -> bool:
        return self.role == UserPermissionRoleEnum.organizer and self.organization_id is not None

    @property
    def is_controller(self) -> bool:
        return self.role == UserPermissionRoleEnum.controller
