import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from src.application.schemas.response import StatisticResponse, SuccessResponse, ErrorResponse
from src.application.services.scan.statistic_service import StatisticService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth import ScanAuthContext
from src.infrastructure.dependencies.scan_di import get_statistic_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/ticket/statistic/{session_id}",
    response_model=SuccessResponse[StatisticResponse],
    summary="Получить статистику сессии",
    description="Возвращает статистику продаж и билетов для указанной сессии.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Не авторизован",
        },
        403: {
            "model": ErrorResponse,
            "description": "Нет доступа",
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
async def get_statistics(
    session_id: Annotated[int, Path(description="ID сессии")],
    auth: ScanAuthContext,
    statistic_service: StatisticService = Depends(get_statistic_service),
):
    try:
        response = await statistic_service.get_session_statistics(session_id=session_id)
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Statistics error: {e.message}")
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
