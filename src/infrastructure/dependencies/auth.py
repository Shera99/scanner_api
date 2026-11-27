import logging
import time
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from src.infrastructure.database.features import db_features
from src.infrastructure.database.models.country import Country
from src.infrastructure.database.models.user import User, UserPermission
from src.infrastructure.database.repos.user import UserRepository
from src.core.entities.zone import ScanZone
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
        scan_zone: ScanZone | None = None,
        password_changed_at: datetime | None = None,
    ):
        self.user = user
        self.permission = permission
        self.country = country
        self.scan_zone = scan_zone
        self.password_changed_at = password_changed_at


# Учётка контролёра нужна на каждый запрос сканера, а меняется редко: держим её
# в памяти процесса. Правка прав или зоны в админке доходит до сканера не позже
# чем через settings.auth_cache_ttl секунд.
_AUTH_CACHE_MAX = 2048
_auth_cache: dict[tuple[int, int], tuple[float, AuthContext]] = {}


def _cached_auth(key: tuple[int, int]) -> AuthContext | None:
    entry = _auth_cache.get(key)
    if entry is not None and entry[0] > time.monotonic():
        return entry[1]
    return None


def _cache_auth(key: tuple[int, int], auth: AuthContext) -> None:
    if len(_auth_cache) >= _AUTH_CACHE_MAX:
        _auth_cache.clear()
    _auth_cache[key] = (time.monotonic() + settings.auth_cache_ttl, auth)


async def _load_permission(session: AsyncSession, user_id: int, permission_id: int) -> UserPermission | None:
    user = joinedload(UserPermission.user)
    if db_features.password_changed_at:
        user = user.undefer(User.password_changed_at)
    options = [user]
    if settings.scan_zone_columns:
        options.append(undefer(UserPermission.scan_zone))

    result = await session.execute(
        select(UserPermission)
        .options(*options)
        .where(
            UserPermission.id == permission_id,
            UserPermission.user_id == user_id,
        )
    )
    return result.scalars().first()


def _reject_if_password_changed(auth: AuthContext, token_data: dict) -> None:
    """Вход, выданный до смены пароля, не действует — правило то же, что в
    showgo_api. Токен без времени выдачи (старый) считается выданным раньше,
    но только у тех, кто пароль менял."""
    if auth.password_changed_at is None:
        return
    issued_at = token_data.get("iat")
    if issued_at is None or \
            datetime.fromtimestamp(issued_at, tz=timezone.utc).replace(tzinfo=None) < auth.password_changed_at:
        raise NotAuthorizedException("password_changed")


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
        cache_key = (user_id, permission_id)
        cached = _cached_auth(cache_key)
        if cached is not None:
            _reject_if_password_changed(cached, token_data)
            return cached

        permission = await _load_permission(session, user_id, permission_id)
        if permission is None:
            # Админка при правке сотрудника удаляет его права и создаёт заново:
            # id из токена пропадает, хотя доступ остался. Берём действующее
            # право — то же, что выдал бы новый вход, — и контролёр остаётся
            # в приложении. Если доступ к сканеру сняли, права не найдётся.
            current = await UserRepository(session).get_scanner_permission(user_id)
            if current is not None:
                permission = await _load_permission(session, user_id, current.id)

        if permission and permission.user:
            scan_zone = ScanZone.parse(permission.scan_zone) if settings.scan_zone_columns else None
            auth = AuthContext(
                user=permission.user,
                permission=permission,
                country=country,
                scan_zone=scan_zone,
                password_changed_at=permission.user.password_changed_at if db_features.password_changed_at else None,
            )
            if settings.auth_cache_ttl > 0:
                session.expunge(permission.user)
                session.expunge(permission)
                _cache_auth(cache_key, auth)
            _reject_if_password_changed(auth, token_data)
            return auth

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
