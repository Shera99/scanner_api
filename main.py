import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_redoc_html

from src.presentation.v1 import router as v1_router
from src.core.config import settings
from src.core.logging import setup_logging
from src.core.exceptions import AppException
from src.application.schemas.response import ErrorResponse
from src.infrastructure.database.session import init_db, close_db
from src.infrastructure.middleware import AuthMiddleware, RequestLoggingMiddleware

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Scanner API v%s", settings.app_version)
    await init_db()
    yield
    await close_db()
    logger.info("Scanner API stopped")


app = FastAPI(
    title="Scanner API",
    description="""
## Scanner API для сканирования билетов

API сервис для мобильного приложения сканера билетов.

### Основные возможности:
- **Аутентификация** — авторизация пользователей с JWT токенами
- **Сканирование билетов** — проверка и отметка билетов при входе/выходе
- **Списки мероприятий** — получение списка доступных для сканирования сессий
- **Статистика** — просмотр статистики продаж и сканирования

### Авторизация:
Для доступа к защищённым эндпоинтам необходимо передать JWT токен в заголовке:
```
Authorization: Bearer <token>
```
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    lifespan=lifespan,
    swagger_ui_parameters={"deepLinking": True, "syntaxHighlight.theme": "obsidian"},
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js",
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            details={"message": exc.message},
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    content = ErrorResponse(
        error="SERVER_ERROR",
        details={"type": exc.__class__.__name__, "message": str(exc)} if settings.debug else None,
    ).model_dump()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )


@app.get("/", tags=["Health"], summary="Root endpoint")
async def root():
    return {
        "service": "Scanner API",
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health", tags=["Health"], summary="Health check")
async def health_check():
    return {
        "status": "ok",
        "service": "scanner",
        "version": settings.app_version,
    }


app.include_router(v1_router, prefix="/api")
