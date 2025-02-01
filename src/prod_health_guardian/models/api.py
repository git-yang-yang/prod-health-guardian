"""API response models."""

from typing import Any, Optional

from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str = "healthy"
    version: str
    error: Optional[str] = None
    system: Optional[dict[str, str]] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str


class MetricsResponse(BaseModel):
    """Metrics response model."""

    metrics: dict[str, Any]
