import logging

from fastapi import APIRouter, Depends, HTTPException

from src.application.schemas.request import AuthRequest
from src.application.schemas.response import AuthResponse, SuccessResponse, ErrorResponse
from src.application.services.auth.service import AuthService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth_di import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=SuccessResponse[AuthResponse],
    summary="Аутентификация пользователя",
    description="Аутентификация по email и паролю. Возвращает данные пользователя и JWT токен.",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Неверный пароль",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": "BadRequestException", "details": {
                        "message": "wrong_password"
                    }}
                }
            }
        },
        403: {
            "model": ErrorResponse,
            "description": "Доступ запрещён",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": "AccessDeniedException", "details": {
                        "message": "access_denied"
                    }}
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Внутренняя ошибка сервера",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": "ServerError", "details": {
                        "message": "Internal server error"
                    }}
                }
            }
        },
    },
)
async def authenticate(
    request: AuthRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        response = await auth_service.authenticate(email=request.email, password=request.password)
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Auth error: {e.message}")
        raise HTTPException(
            status_code=e.code,
            detail=ErrorResponse(
                error=e.__class__.__name__,
                details={"message": e.message},
            ).model_dump(),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(error="ServerError", details={"message": str(e)}).model_dump(),
        )
