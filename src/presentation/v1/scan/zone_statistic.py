import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from src.application.schemas.response import ZoneStatisticResponse, SuccessResponse, ErrorResponse
from src.application.services.scan.zone_service import ZoneService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth import ScanAuthContext
from src.infrastructure.dependencies.scan_di import get_zone_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/zone/statistic/{session_id}",
    response_model=SuccessResponse[ZoneStatisticResponse],
    summary="Статистика сеанса по зонам",
    description=(
        "Сколько билетов всего, сколько пришло, сколько сейчас внутри и сколько "
        "осталось — по всему сеансу, по зонам контролёров, по типам билетов, "
        "областям схемы и секторам.\n\n"
        "Из этих же строк собирается зона сканирования. Если `zone_locked` = true, "
        "зона закреплена за учёткой в админке и выбор в приложении не показывается. "
        "Иначе контролёр отмечает нужные строки, а приложение передаёт выбор "
        "в поле `zone` запроса `/check`."
    ),
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
async def get_zone_statistic(
    session_id: Annotated[int, Path(description="ID сессии")],
    auth: ScanAuthContext,
    zone_service: ZoneService = Depends(get_zone_service),
):
    try:
        response = await zone_service.get_statistics(
            session_id=session_id,
            account_zone=auth.scan_zone,
        )
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Zone statistic error: {e.message}")
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
