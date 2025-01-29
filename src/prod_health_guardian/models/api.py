"""Models for API requests and responses."""

from typing import Union

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(
        ...,
        description="Error message",
        json_schema_extra={
            "example": "Resource not found"
        }
    )


class HealthStatus(BaseModel):
    """Health status response model."""

    status: str = Field(
        ...,
        description="Health status",
        json_schema_extra={
            "example": "healthy"
        }
    )
    version: str = Field(
        ...,
        description="API version",
        json_schema_extra={
            "example": "0.1.0"
        }
    )
    system: dict[str, str] = Field(
        ...,
        description="System component statuses",
        json_schema_extra={
            "example": {
                "api": "running",
                "collectors": "ready"
            }
        }
    )


class MetricsResponse(BaseModel):
    """Metrics response model."""

    metrics: dict[str, dict[str, Union[int, float, dict, list]]] = Field(
        ...,
        description="Metrics from collectors",
        json_schema_extra={
            "example": {
                "cpu": {
                    "count": {"physical": 4, "logical": 8},
                    "percent": {"total": 25.5, "per_cpu": [20.0, 30.0]}
                },
                "memory": {
                    "virtual": {"total": 16_000_000_000, "percent": 43.75},
                    "swap": {"total": 8_000_000_000, "percent": 12.5}
                }
            }
        }
    ) 