from typing import Optional

from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.repositories.user import AbstractUserRepository, SCANNER_ROLES
from src.infrastructure.database.models.user import User, UserPermission
from src.infrastructure.database.repos.base import BaseRepository

ROLE_PRIORITY = {role: idx for idx, role in enumerate(SCANNER_ROLES)}


class UserRepository(BaseRepository[User], AbstractUserRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(
                User.email == email,
                User.encrypted_password.is_not(None),
            )
        )
        return result.scalars().first()

    async def get_by_email_strict(self, email: str) -> User:
        result = await self.session.execute(
            select(User).where(
                User.email == email,
                User.encrypted_password.is_not(None),
            )
        )
        return result.scalars().one()

    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalars().first()

    async def get_by_uuid(self, uuid: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.uuid == uuid)
        )
        return result.scalars().first()

    async def get_scanner_permission(
        self, user_id: int,
    ) -> Optional[UserPermission]:
        """Return the highest-priority scanner permission (no country_id filter)."""
        priority_order = case(
            *[(UserPermission.role == role, idx) for role, idx in ROLE_PRIORITY.items()],
            else_=999,
        )
        result = await self.session.execute(
            select(UserPermission)
            .where(
                UserPermission.user_id == user_id,
                UserPermission.role.in_(SCANNER_ROLES),
            )
            .order_by(priority_order)
            .limit(1)
        )
        return result.scalars().first()

    async def get_permission_by_id(self, permission_id: int) -> Optional[UserPermission]:
        result = await self.session.execute(
            select(UserPermission).where(UserPermission.id == permission_id)
        )
        return result.scalars().first()
