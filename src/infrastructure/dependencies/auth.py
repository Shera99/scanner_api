import logging
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.country import Country
from src.infrastructure.database.models.user import User, UserPermission
from src.core.enums.user import UserPermissionRoleEnum
from src.core.config import settings
from src.core.exceptions import (
    AccessDeniedException,
    NotAuthorizedException,
)
from src.infrastructure.database.session import get_session

logger = logging.getLogger(__name__)

_country_cache: Country | None = None


async def get_country(session: AsyncSession = Depends(get_session)) -> Country:
    global _country_cache
    if _country_cache is not None:
        return _country_cache

    result = await session.execute(
        select(Country).where(Country.code == settings.default_country_code)
    )
    country = result.scalars().first()
    if not country:
        result = await session.execute(
            select(Country).where(Country.id == settings.default_country_id)
        )
        country = result.scalars().first()

    if country:
        session.expunge(country)
        _country_cache = country
    return country


CurrentCountry = Annotated[Country, Depends(get_country)]


class AuthContext:

    def __init__(
        self,
        user: User,
        permission: UserPermission | None = None,
        country: Country | None = None,
    ):
        self.user = user
        self.permission = permission
        self.country = country


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    country: Country = Depends(get_country),
) -> AuthContext:
    token_data: dict | None = getattr(request.state, "token_data", None)
    if not token_data:
        raise NotAuthorizedException()

    user_id = token_data.get("id")
    if not user_id:
        raise NotAuthorizedException("Invalid token payload")

    permission_id = token_data.get("permission_id")

    if permission_id:
        from sqlalchemy.orm import joinedload
        result = await session.execute(
            select(UserPermission)
            .options(joinedload(UserPermission.user))
            .where(
                UserPermission.id == permission_id,
                UserPermission.user_id == user_id,
            )
        )
        permission = result.scalars().first()
        if permission and permission.user:
            return AuthContext(user=permission.user, permission=permission, country=country)

        logger.warning("Permission id=%s not found for user_id=%s", permission_id, user_id)

    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise NotAuthorizedException()

    return AuthContext(user=user, permission=None, country=country)


CurrentUser = Annotated[AuthContext, Depends(get_current_user)]


class RoleChecker:

    def __init__(self, allowed_roles: list[UserPermissionRoleEnum] | None = None):
        self.allowed_roles = allowed_roles

    def __call__(self, auth: CurrentUser) -> AuthContext:
        if not auth.user:
            raise NotAuthorizedException()

        logger.debug(
            "Auth: user_id=%s, permission=%s (role=%s)",
            auth.user.id,
            auth.permission.id if auth.permission else None,
            auth.permission.role.value if auth.permission else None,
        )

        if self.allowed_roles:
            if auth.permission is None:
                logger.warning("RoleChecker: permission is None for user_id=%s", auth.user.id)
                raise AccessDeniedException("The user has no permission")
            if auth.permission.role not in self.allowed_roles:
                logger.warning(
                    "RoleChecker: role %s not in allowed %s for user_id=%s",
                    auth.permission.role.value, [r.value for r in self.allowed_roles], auth.user.id,
                )
                raise AccessDeniedException("The user has no permission")

        return auth


def require_scan_roles() -> RoleChecker:
    return RoleChecker(allowed_roles=[
        UserPermissionRoleEnum.controller,
        UserPermissionRoleEnum.super_admin,
        UserPermissionRoleEnum.admin,
        UserPermissionRoleEnum.manager,
    ])


ScanAuthContext = Annotated[AuthContext, Depends(require_scan_roles())]
