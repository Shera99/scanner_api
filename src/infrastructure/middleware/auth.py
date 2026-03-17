import logging

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from src.application.schemas.response import ErrorResponse
from src.infrastructure.security import decode_token

logger = logging.getLogger(__name__)

PUBLIC_PATHS = frozenset({
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
})

PUBLIC_PREFIXES = (
    "/docs",
)

PUBLIC_EXACT_ROUTES: dict[tuple[str, str], bool] = {
    ("POST", "/api/v1/auth"): True
}


def _is_public(method: str, path: str) -> bool:
    if method == "OPTIONS":
        return True
    if path in PUBLIC_PATHS:
        return True
    if any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
        return True
    if (method, path) in PUBLIC_EXACT_ROUTES:
        return True
    return False


def _error_response(message: str, error: str = "NotAuthorizedException") -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse(
            error=error,
            details={"message": message},
        ).model_dump(),
    )


class AuthMiddleware:
    """Pure ASGI middleware — no BaseHTTPMiddleware, no greenlet issues."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        path = scope.get("path", "/")

        if _is_public(method, path):
            await self.app(scope, receive, send)
            return

        headers = dict(
            (k.decode("latin-1"), v.decode("latin-1"))
            for k, v in scope.get("headers", [])
        )
        auth_header = headers.get("authorization")

        if not auth_header:
            response = _error_response("Authorization header is missing")
            await response(scope, receive, send)
            return

        if not auth_header.startswith("Bearer "):
            response = _error_response("Invalid authorization header format", "InvalidTokenException")
            await response(scope, receive, send)
            return

        token = auth_header[7:]
        if not token:
            response = _error_response("Token is empty")
            await response(scope, receive, send)
            return

        try:
            token_data = decode_token(token)
        except Exception as e:
            logger.warning("JWT decode failed for %s %s: %s", method, path, e)
            response = _error_response("Token is invalid or expired", "InvalidTokenException")
            await response(scope, receive, send)
            return

        logger.debug("Auth OK for %s %s | user_id=%s permission_id=%s",
                      method, path, token_data.get("id"), token_data.get("permission_id"))
        scope.setdefault("state", {})["token_data"] = token_data
        await self.app(scope, receive, send)
