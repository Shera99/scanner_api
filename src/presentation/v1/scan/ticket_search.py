import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from src.application.schemas.response import TicketResponse, SuccessResponse, ErrorResponse
from src.application.services.scan.ticket_service import TicketService
from src.core.exceptions import AppException
from src.infrastructure.dependencies.auth import ScanAuthContext
from src.infrastructure.dependencies.scan_di import get_ticket_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/ticket/search/{session_id}/{ticket_number}",
    response_model=SuccessResponse[TicketResponse],
    summary="Поиск билета по номеру",
    description="Поиск билета по серийному номеру в рамках сессии.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Билет не найден",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": "NotFoundException", "details": {
                        "message": "Билет не найден!"
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
async def search_ticket(
    session_id: Annotated[int, Path(description="ID сессии")],
    ticket_number: Annotated[str, Path(description="Серийный номер билета")],
    auth: ScanAuthContext,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        response = await ticket_service.search_ticket(
            session_id=session_id,
            ticket_number=ticket_number,
        )
        return SuccessResponse(data=response)
    except AppException as e:
        logger.error(f"Ticket search error: {e.message}")
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
