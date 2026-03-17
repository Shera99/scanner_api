from fastapi import APIRouter

from src.presentation.v1.auth import authenticate

router = APIRouter(tags=["Authentication"])

router.include_router(authenticate.router)
