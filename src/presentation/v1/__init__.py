"""API v1 router combining all endpoints."""
from fastapi import APIRouter

from src.presentation.v1 import auth, scan

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(scan.router)
