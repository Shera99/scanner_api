import logging

from fastapi import APIRouter, Depends, HTTPException

from src.application.schemas.request import ScanCheckRequest
from src.application.schemas.response import CheckResultResponse, SuccessResponse, ErrorResponse
from src.application.services.scan.check_service import ScanCheckService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth import ScanAuthContext
from src.infrastructure.dependencies.scan_di import get_scan_check_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/check",
    response_model=SuccessResponse[CheckResultResponse],
    summary="Проверить и отсканировать билет",
    description=(
        "Проверяет валидность билета и отмечает его как отсканированный. "
        "Всегда возвращает 200 с полем `status`: "
        "`allowed`, `already_used`, `error_invalid`, `wrong_event`."
    ),
    responses={
        200: {
            "description": "Результат сканирования",
            "content": {
                "application/json": {
                    "examples": {
                        "allowed": {
                            "summary": "Проход разрешён",
                            "value": {
                                "success": True,
                                "data": {
                                    "status": "allowed",
                                    "message": "ПРОХОД РАЗРЕШЁН",
                                    "place": "Сектор A · Ряд 5 · Место 18",
                                    "event_name": "JONY — Дворец профсоюзов",
                                    "event_date": "10.03.2026",
                                    "counts": {"all_count": 100, "scan_count": 42, "in_count": 40, "out_count": 2},
                                },
                            },
                        },
                        "already_used": {
                            "summary": "Уже использован",
                            "value": {
                                "success": True,
                                "data": {
                                    "status": "already_used",
                                    "message": "УЖЕ ИСПОЛЬЗОВАН",
                                    "place": "Сектор A · Ряд 5 · Место 18",
                                    "first_check_in": "19:12:03",
                                    "scanned_by": "scanner_01",
                                },
                            },
                        },
                        "wrong_event": {
                            "summary": "Не для этого мероприятия",
                            "value": {
                                "success": True,
                                "data": {
                                    "status": "wrong_event",
                                    "message": "НЕ ДЛЯ ЭТОГО МЕРОПРИЯТИЯ",
                                    "event_name": "JONY — Дворец профсоюзов",
                                    "event_date": "10.03.2026",
                                },
                            },
                        },
                        "error_invalid": {
                            "summary": "Ошибка / недействителен",
                            "value": {
                                "success": True,
                                "data": {
                                    "status": "error_invalid",
                                    "message": "ОШИБКА / НЕДЕЙСТВИТЕЛЕН",
                                    "reason": "Билет отменен (возврат)",
                                },
                            },
                        },
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Внутренняя ошибка сервера",
        },
    },
)
async def check_ticket(
    request: ScanCheckRequest,
    auth: ScanAuthContext,
    check_service: ScanCheckService = Depends(get_scan_check_service),
):
    try:
        time_zone_diff = None
        if auth.country:
            time_zone_diff = auth.country.time_zone_difference

        response = await check_service.check_ticket(
            session_id=request.data.session_id,
            scan_type=request.data.type,
            user_id=auth.user.id,
            code=request.data.code,
            no_code=request.data.no_code,
            time_zone_difference=time_zone_diff,
        )
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Check ticket error: {e.message}")
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
