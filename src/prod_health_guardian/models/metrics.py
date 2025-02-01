"""Models for system metrics data."""

from pydantic import BaseModel, Field


class CPUMetrics(BaseModel):
    """CPU metrics model."""

    physical_cores: int = Field(
        ...,
        description="Number of physical CPU cores",
        json_schema_extra={"example": 4},
    )
    logical_cores: int = Field(
        ...,
        description="Number of logical CPU cores",
        json_schema_extra={"example": 8},
    )
    cpu_freq_current: float = Field(
        ...,
        description="Current CPU frequency in MHz",
        json_schema_extra={"example": 2400.0},
    )
    cpu_freq_min: float = Field(
        ...,
        description="Minimum CPU frequency in MHz",
        json_schema_extra={"example": 2200.0},
    )
    cpu_freq_max: float = Field(
        ...,
        description="Maximum CPU frequency in MHz",
        json_schema_extra={"example": 3200.0},
    )
    cpu_percent: float = Field(
        ...,
        description="Total CPU usage percentage",
        json_schema_extra={"example": 25.5},
    )
    per_cpu_percent: list[float] = Field(
        ...,
        description="CPU usage percentage per core",
        json_schema_extra={"example": [20.0, 30.0, 25.0, 27.0]},
    )
    ctx_switches: int = Field(
        ...,
        description="Total number of context switches",
        json_schema_extra={"example": 1000},
    )
    interrupts: int = Field(
        ...,
        description="Total number of interrupts",
        json_schema_extra={"example": 500},
    )
    soft_interrupts: int = Field(
        ...,
        description="Total number of soft interrupts",
        json_schema_extra={"example": 200},
    )
    syscalls: int = Field(
        ...,
        description="Total number of system calls",
        json_schema_extra={"example": 5000},
    )


class MemoryMetrics(BaseModel):
    """Memory metrics model."""

    total: int = Field(
        ...,
        description="Total virtual memory in bytes",
        json_schema_extra={"example": 16_000_000_000},
    )
    available: int = Field(
        ...,
        description="Available virtual memory in bytes",
        json_schema_extra={"example": 8_000_000_000},
    )
    used: int = Field(
        ...,
        description="Used virtual memory in bytes",
        json_schema_extra={"example": 7_000_000_000},
    )
    free: int = Field(
        ...,
        description="Free virtual memory in bytes",
        json_schema_extra={"example": 1_000_000_000},
    )
    percent: float = Field(
        ...,
        description="Virtual memory usage percentage",
        json_schema_extra={"example": 43.75},
    )
    swap_total: int = Field(
        ...,
        description="Total swap memory in bytes",
        json_schema_extra={"example": 8_000_000_000},
    )
    swap_used: int = Field(
        ...,
        description="Used swap memory in bytes",
        json_schema_extra={"example": 1_000_000_000},
    )
    swap_free: int = Field(
        ...,
        description="Free swap memory in bytes",
        json_schema_extra={"example": 7_000_000_000},
    )
    swap_percent: float = Field(
        ...,
        description="Swap memory usage percentage",
        json_schema_extra={"example": 12.5},
    )
    swap_in: int = Field(
        ...,
        description="Number of memory pages swapped in",
        json_schema_extra={"example": 100},
    )
    swap_out: int = Field(
        ...,
        description="Number of memory pages swapped out",
        json_schema_extra={"example": 50},
    )


class GPUMetrics(BaseModel):
    """GPU metrics model."""

    name: str = Field(
        ...,
        description="GPU device name",
        json_schema_extra={"example": "NVIDIA GeForce RTX 3080"},
    )
    temperature: float = Field(
        ...,
        description="GPU temperature in Celsius",
        json_schema_extra={"example": 65.0},
    )
    power_watts: float = Field(
        ...,
        description="GPU power usage in Watts",
        json_schema_extra={"example": 220.5},
    )
    memory_total: int = Field(
        ...,
        description="Total GPU memory in bytes",
        json_schema_extra={"example": 10_737_418_240},  # 10GB
    )
    memory_used: int = Field(
        ...,
        description="Used GPU memory in bytes",
        json_schema_extra={"example": 4_294_967_296},  # 4GB
    )
    memory_free: int = Field(
        ...,
        description="Free GPU memory in bytes",
        json_schema_extra={"example": 6_442_450_944},  # 6GB
    )
    gpu_utilization: float = Field(
        ...,
        description="GPU utilization percentage",
        json_schema_extra={"example": 85.5},
    )
    memory_utilization: float = Field(
        ...,
        description="GPU memory utilization percentage",
        json_schema_extra={"example": 40.0},
    )
    fan_speed: float = Field(
        ...,
        description="GPU fan speed percentage",
        json_schema_extra={"example": 75.0},
    )


class SystemMetrics(BaseModel):
    """System metrics model."""

    cpu: CPUMetrics = Field(
        ...,
        description="CPU metrics",
    )
    memory: MemoryMetrics = Field(
        ...,
        description="Memory metrics",
    )
    gpu: GPUMetrics = Field(
        ...,
        description="GPU metrics",
    )
