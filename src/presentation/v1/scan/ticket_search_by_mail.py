import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from src.application.schemas.response import TicketListResponse, SuccessResponse, ErrorResponse
from src.application.services.scan.ticket_service import TicketService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth import ScanAuthContext
from src.infrastructure.dependencies.scan_di import get_ticket_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/ticket/search/by_mail/{session_id}/{email}",
    response_model=SuccessResponse[TicketListResponse],
    summary="Поиск билетов по email",
    description="Поиск билетов по email пользователя в рамках сессии. Возвращает все билеты, привязанные к заказам с указанным email.",
    responses={
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
async def search_ticket_by_mail(
    session_id: Annotated[int, Path(description="ID сессии")],
    email: Annotated[str, Path(description="Email пользователя")],
    auth: ScanAuthContext,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        response = await ticket_service.search_tickets_by_email(
            session_id=session_id,
            email=email,
        )
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Ticket search by mail error: {e.message}")
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
