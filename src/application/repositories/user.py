from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from src.application.repositories.base import IBaseRepository
from src.core.enums.user import UserPermissionRoleEnum

if TYPE_CHECKING:
    from src.infrastructure.database.models.user import User, UserPermission


SCANNER_ROLES = [
    UserPermissionRoleEnum.super_admin,
    UserPermissionRoleEnum.admin,
    UserPermissionRoleEnum.manager,
    UserPermissionRoleEnum.controller,
]

FULL_ACCESS_ROLES = [
    UserPermissionRoleEnum.super_admin,
    UserPermissionRoleEnum.admin,
    UserPermissionRoleEnum.manager,
]


class AbstractUserRepository(IBaseRepository["User"], ABC):

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional["User"]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email_strict(self, email: str) -> "User":
        raise NotImplementedError

    @abstractmethod
    async def get_by_phone_number(self, phone_number: str) -> Optional["User"]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_uuid(self, uuid: str) -> Optional["User"]:
        raise NotImplementedError

    @abstractmethod
    async def get_scanner_permission(
        self, user_id: int,
    ) -> Optional["UserPermission"]:
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_id(self, permission_id: int) -> Optional["UserPermission"]:
        raise NotImplementedError
