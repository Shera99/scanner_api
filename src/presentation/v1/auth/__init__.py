from fastapi import APIRouter

from src.presentation.v1.auth import authenticate

router = APIRouter(prefix="/auth", tags=["Authentication"])

router.include_router(authenticate.router)
