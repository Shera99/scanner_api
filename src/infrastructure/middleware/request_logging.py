import json
import logging
import time
import traceback

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("api.request")

SKIP_PATHS = frozenset({"/", "/health", "/docs", "/openapi.json", "/redoc"})
MAX_BODY_LOG = 2048


def _mask_token(value: str) -> str:
    if value.startswith("Bearer ") and len(value) > 20:
        return f"Bearer ...{value[-8:]}"
    return value


def _parse_headers(raw_headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
    headers = {}
    for k, v in raw_headers:
        name = k.decode("latin-1")
        val = v.decode("latin-1")
        if name == "authorization":
            val = _mask_token(val)
        headers[name] = val
    return headers


def _safe_body_str(body: bytes) -> str:
    if not body:
        return ""
    text = body[:MAX_BODY_LOG].decode("utf-8", errors="replace")
    if len(body) > MAX_BODY_LOG:
        text += f"... (truncated, total {len(body)} bytes)"
    return text


class RequestLoggingMiddleware:
    """Pure ASGI middleware that logs every API request with body, headers, and response status."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "/")
        if path in SKIP_PATHS or path.startswith("/docs"):
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        headers = _parse_headers(scope.get("headers", []))
        client = scope.get("client")
        client_ip = client[0] if client else "-"

        body_chunks: list[bytes] = []

        async def receive_wrapper():
            message = await receive()
            if message.get("type") == "http.request":
                body_chunks.append(message.get("body", b""))
            return message

        response_status = 0
        start = time.perf_counter()

        async def send_wrapper(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            await send(message)

        exc_info = None
        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        except Exception as e:
            exc_info = e
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            body_text = _safe_body_str(b"".join(body_chunks))

            log_data = {
                "method": method,
                "path": path,
                "client": client_ip,
                "status": response_status,
                "duration_ms": round(elapsed_ms, 1),
                "headers": {
                    k: v for k, v in headers.items()
                    if k in ("authorization", "content-type", "user-agent", "x-forwarded-for")
                },
            }
            if body_text:
                log_data["body"] = body_text

            if exc_info:
                log_data["error"] = f"{exc_info.__class__.__name__}: {exc_info}"
                log_data["traceback"] = traceback.format_exc()
                logger.error(
                    "%s %s → %s (%.1fms) ERROR: %s",
                    method, path, response_status, elapsed_ms, exc_info,
                    extra={"request_data": log_data},
                )
            elif response_status >= 400:
                logger.warning(
                    "%s %s → %s (%.1fms) | body=%s",
                    method, path, response_status, elapsed_ms, body_text or "-",
                    extra={"request_data": log_data},
                )
            else:
                logger.info(
                    "%s %s → %s (%.1fms)",
                    method, path, response_status, elapsed_ms,
                    extra={"request_data": log_data},
                )
