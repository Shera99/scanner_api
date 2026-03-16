from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auth.service import AuthService
from src.infrastructure.database.repos.user import UserRepository
from src.infrastructure.database.session import get_session


async def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(
        user_repo=UserRepository(session),
        db_session=session,
    )
