import logging

from fastapi import APIRouter, Depends, HTTPException

from src.application.schemas.response import EventListResponse, SuccessResponse, ErrorResponse
from src.application.services.scan.event_service import EventService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth import ScanAuthContext
from src.infrastructure.dependencies.scan_di import get_event_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/event/list",
    response_model=SuccessResponse[EventListResponse],
    summary="Получить список мероприятий для сканирования",
    description="Возвращает список мероприятий/сессий, доступных для сканирования на основе прав пользователя.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Не авторизован",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": "NotAuthorizedException", "details": {
                        "message": "User not authorized"
                    }}
                }
            }
        },
        403: {
            "model": ErrorResponse,
            "description": "Нет доступа",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": "AccessDeniedException", "details": {
                        "message": "The user has no permission"
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
async def get_events(
    auth: ScanAuthContext,
    event_service: EventService = Depends(get_event_service),
):
    try:
        response = await event_service.get_events_for_permission(permission=auth.permission)
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Events error: {e.message}")
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
