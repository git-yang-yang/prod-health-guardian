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


class GPUDeviceMetrics(BaseModel):
    """GPU device metrics model."""

    name: str = Field(
        ...,
        description="GPU device name",
        json_schema_extra={
            "example": "NVIDIA GeForce RTX 3080"
        }
    )
    temperature: float = Field(
        ...,
        description="GPU temperature in Celsius",
        json_schema_extra={
            "example": 65.0
        }
    )
    power_usage: float = Field(
        ...,
        description="GPU power usage in Watts",
        json_schema_extra={
            "example": 220.5
        }
    )
    memory_total: int = Field(
        ...,
        description="Total GPU memory in bytes",
        json_schema_extra={
            "example": 10_737_418_240  # 10GB
        }
    )
    memory_used: int = Field(
        ...,
        description="Used GPU memory in bytes",
        json_schema_extra={
            "example": 4_294_967_296  # 4GB
        }
    )
    memory_free: int = Field(
        ...,
        description="Free GPU memory in bytes",
        json_schema_extra={
            "example": 6_442_450_944  # 6GB
        }
    )
    utilization: float = Field(
        ...,
        description="GPU utilization percentage",
        json_schema_extra={
            "example": 85.5
        }
    )
    memory_utilization: float = Field(
        ...,
        description="GPU memory utilization percentage",
        json_schema_extra={
            "example": 40.0
        }
    )
    fan_speed: float = Field(
        ...,
        description="GPU fan speed percentage",
        json_schema_extra={
            "example": 75.0
        }
    )


class GPUMetrics(BaseModel):
    """GPU metrics model."""

    device_count: int = Field(
        ...,
        description="Number of GPU devices",
        json_schema_extra={
            "example": 2
        }
    )
    devices: list[GPUDeviceMetrics] = Field(
        ...,
        description="List of GPU device metrics",
        json_schema_extra={
            "example": [{
                "name": "NVIDIA GeForce RTX 3080",
                "temperature": 65.0,
                "power_usage": 220.5,
                "memory_total": 10_737_418_240,
                "memory_used": 4_294_967_296,
                "memory_free": 6_442_450_944,
                "utilization": 85.5,
                "memory_utilization": 40.0,
                "fan_speed": 75.0
            }]
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
    gpu: GPUMetrics = Field(
        ...,
        description="GPU metrics"
    ) 