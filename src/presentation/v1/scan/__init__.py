"""Scan presentation endpoints."""
from fastapi import APIRouter

from src.presentation.v1.scan import (
    status,
    events,
    check,
    ticket_list,
    ticket_search,
    ticket_search_by_mail,
    statistics,
)

router = APIRouter(tags=["Scan"])

router.include_router(status.router)
router.include_router(events.router)
router.include_router(check.router)
router.include_router(ticket_list.router)
router.include_router(ticket_search.router)
router.include_router(ticket_search_by_mail.router)
router.include_router(statistics.router)
