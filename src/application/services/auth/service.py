from sqlalchemy.ext.asyncio import AsyncSession

from src.application.repositories.user import AbstractUserRepository
from src.core.exceptions import AccessDeniedException, BadRequestException
from src.infrastructure.security import check_password, create_access_token
from src.application.schemas.response import AuthResponse, UserResponse


class AuthService:

    def __init__(self, user_repo: AbstractUserRepository, db_session: AsyncSession):
        self.user_repo = user_repo
        self.db_session = db_session

    async def authenticate(self, email: str, password: str) -> AuthResponse:
        user = await self.user_repo.get_by_email_strict(email)

        if not check_password(password, user.encrypted_password):
            raise BadRequestException("wrong_password")

        permission = await self.user_repo.get_scanner_permission(user_id=user.id)
        if not permission:
            raise AccessDeniedException("access_denied")

        token = create_access_token({
            "id": user.id,
            "permission_id": permission.id,
        })

        user_response = UserResponse(
            id=user.id,
            email=user.email,
            phone_number=user.phone_number,
            full_name=user.full_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        return AuthResponse(
            user=user_response,
            token=token,
            role=permission.role.value,
        )
