from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Unified success response wrapper."""
    success: bool = Field(default=True)
    data: T | None = Field(default=None, description="Response payload")


class ErrorResponse(BaseModel):
    """Unified error response wrapper."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error class/code")
    details: dict | None = Field(default=None, description="Error details")


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "scanner"
    version: str = "1.0.0"
