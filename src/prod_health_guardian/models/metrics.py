"""Models for system metrics data."""

from typing import Optional, Union

from pydantic import BaseModel, Field


class CPUMetrics(BaseModel):
    """CPU metrics model."""

    count: dict[str, int] = Field(
        ...,
        description="CPU core counts",
        json_schema_extra={
            "example": {"physical": 4, "logical": 8}
        }
    )
    frequency: dict[str, Optional[float]] = Field(
        ...,
        description="CPU frequencies in MHz",
        json_schema_extra={
            "example": {
                "current": 2400.0,
                "min": 2200.0,
                "max": 3200.0
            }
        }
    )
    percent: dict[str, Union[float, list[float]]] = Field(
        ...,
        description="CPU usage percentages",
        json_schema_extra={
            "example": {
                "total": 25.5,
                "per_cpu": [20.0, 30.0, 25.0, 27.0]
            }
        }
    )
    stats: dict[str, int] = Field(
        ...,
        description="CPU statistics",
        json_schema_extra={
            "example": {
                "ctx_switches": 1000,
                "interrupts": 500,
                "soft_interrupts": 200,
                "syscalls": 5000
            }
        }
    )


class MemoryMetrics(BaseModel):
    """Memory metrics model."""

    virtual: dict[str, Union[int, float]] = Field(
        ...,
        description="Virtual memory metrics",
        json_schema_extra={
            "example": {
                "total": 16_000_000_000,
                "available": 8_000_000_000,
                "used": 7_000_000_000,
                "free": 1_000_000_000,
                "percent": 43.75
            }
        }
    )
    swap: dict[str, Union[int, float]] = Field(
        ...,
        description="Swap memory metrics",
        json_schema_extra={
            "example": {
                "total": 8_000_000_000,
                "used": 1_000_000_000,
                "free": 7_000_000_000,
                "percent": 12.5,
                "sin": 100,
                "sout": 50
            }
        }
    )


class SystemMetrics(BaseModel):
    """System metrics model."""

    cpu: CPUMetrics = Field(
        ...,
        description="CPU metrics"
    )
    memory: MemoryMetrics = Field(
        ...,
        description="Memory metrics"
    ) 