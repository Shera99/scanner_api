import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.application.schemas.response import TicketListResponse, SuccessResponse, ErrorResponse
from src.application.services.scan.ticket_service import TicketService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth import ScanAuthContext
from src.infrastructure.dependencies.scan_di import get_ticket_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/ticket/list/{session_id}/{last_ticket_id}",
    response_model=SuccessResponse[TicketListResponse],
    summary="Получить список билетов",
    description="Возвращает пагинированный список билетов сессии. Поддерживает фильтрацию по статусу и email.",
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
async def get_ticket_list(
    session_id: Annotated[int, Path(description="ID сессии")],
    last_ticket_id: Annotated[int, Path(description="ID последнего билета для пагинации (0 для первой страницы)")],
    auth: ScanAuthContext,
    ticket_service: TicketService = Depends(get_ticket_service),
    type: Annotated[str | None, Query(description="Фильтр по статусу: scanned или notScanned")] = None,
    email: Annotated[str | None, Query(description="Фильтр по email пользователя")] = None,
):
    try:
        response = await ticket_service.get_ticket_list(
            session_id=session_id,
            last_ticket_id=last_ticket_id,
            scan_status=type,
            email_filter=email,
        )
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Ticket list error: {e.message}")
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
