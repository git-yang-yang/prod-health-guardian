"""Tests for data models."""

from typing import Any

import pytest
from pydantic import ValidationError

from prod_health_guardian import __version__
from prod_health_guardian.models import (
    CPUMetrics,
    ErrorResponse,
    GPUMetrics,
    HealthStatus,
    MemoryMetrics,
    MetricsResponse,
    SystemMetrics,
)

# Test constants
CPU_PHYSICAL_CORES = 4
CPU_LOGICAL_CORES = 8
CPU_FREQ_CURRENT = 2400.0
CPU_FREQ_MIN = 2200.0
CPU_FREQ_MAX = 3200.0
CPU_PERCENT = 25.5
PER_CPU_PERCENT = [20.0, 30.0, 25.0, 27.0]
CTX_SWITCHES = 1000
INTERRUPTS = 500
SOFT_INTERRUPTS = 200
SYSCALLS = 300

# Memory test constants
MEM_TOTAL = 16_000_000_000
MEM_AVAILABLE = 8_000_000_000
MEM_USED = 8_000_000_000
MEM_FREE = 8_000_000_000
MEM_PERCENT = 50.0
MEM_SWAP_TOTAL = 8_000_000_000
MEM_SWAP_USED = 1_000_000_000
MEM_SWAP_FREE = 7_000_000_000
MEM_SWAP_PERCENT = 12.5
MEM_SWAP_IN = 100
MEM_SWAP_OUT = 50

# GPU test constants
GPU_NAME = "NVIDIA GeForce RTX 3080"
GPU_TEMPERATURE = 65.0
GPU_POWER_WATTS = 220.5
GPU_MEMORY_TOTAL = 10_737_418_240  # 10GB
GPU_MEMORY_USED = 4_294_967_296  # 4GB
GPU_MEMORY_FREE = 6_442_450_944  # 6GB
GPU_UTILIZATION = 85.5
GPU_MEMORY_UTILIZATION = 40.0
GPU_FAN_SPEED = 75.0

# Test data
VALID_CPU_DATA = {
    "physical_cores": CPU_PHYSICAL_CORES,
    "logical_cores": CPU_LOGICAL_CORES,
    "cpu_freq_current": CPU_FREQ_CURRENT,
    "cpu_freq_min": CPU_FREQ_MIN,
    "cpu_freq_max": CPU_FREQ_MAX,
    "cpu_percent": CPU_PERCENT,
    "per_cpu_percent": PER_CPU_PERCENT,
    "ctx_switches": CTX_SWITCHES,
    "interrupts": INTERRUPTS,
    "soft_interrupts": SOFT_INTERRUPTS,
    "syscalls": SYSCALLS,
}

VALID_MEMORY_DATA = {
    "total": MEM_TOTAL,
    "available": MEM_AVAILABLE,
    "used": MEM_USED,
    "free": MEM_FREE,
    "percent": MEM_PERCENT,
    "swap_total": MEM_SWAP_TOTAL,
    "swap_used": MEM_SWAP_USED,
    "swap_free": MEM_SWAP_FREE,
    "swap_percent": MEM_SWAP_PERCENT,
    "swap_in": MEM_SWAP_IN,
    "swap_out": MEM_SWAP_OUT,
}

VALID_GPU_DATA = {
    "name": GPU_NAME,
    "temperature": GPU_TEMPERATURE,
    "power_watts": GPU_POWER_WATTS,
    "memory_total": GPU_MEMORY_TOTAL,
    "memory_used": GPU_MEMORY_USED,
    "memory_free": GPU_MEMORY_FREE,
    "gpu_utilization": GPU_UTILIZATION,
    "memory_utilization": GPU_MEMORY_UTILIZATION,
    "fan_speed": GPU_FAN_SPEED,
}


@pytest.fixture
def valid_cpu_metrics() -> dict[str, Any]:
    """Valid CPU metrics fixture.

    Returns:
        dict[str, Any]: Valid CPU metrics data.
    """
    return VALID_CPU_DATA


@pytest.fixture
def valid_memory_metrics() -> dict[str, Any]:
    """Valid memory metrics fixture.

    Returns:
        dict[str, Any]: Valid memory metrics data.
    """
    return VALID_MEMORY_DATA


@pytest.fixture
def valid_gpu_metrics() -> dict[str, Any]:
    """Valid GPU metrics fixture.

    Returns:
        dict[str, Any]: Valid GPU metrics data.
    """
    return VALID_GPU_DATA


def test_cpu_metrics_valid():
    """Test valid CPU metrics."""
    metrics = CPUMetrics(**VALID_CPU_DATA)
    assert metrics.physical_cores == CPU_PHYSICAL_CORES
    assert metrics.logical_cores == CPU_LOGICAL_CORES
    assert metrics.cpu_freq_current == CPU_FREQ_CURRENT
    assert metrics.cpu_freq_min == CPU_FREQ_MIN
    assert metrics.cpu_freq_max == CPU_FREQ_MAX
    assert metrics.cpu_percent == CPU_PERCENT
    assert metrics.per_cpu_percent == PER_CPU_PERCENT
    assert metrics.ctx_switches == CTX_SWITCHES
    assert metrics.interrupts == INTERRUPTS
    assert metrics.soft_interrupts == SOFT_INTERRUPTS
    assert metrics.syscalls == SYSCALLS


def test_cpu_metrics_invalid():
    """Test invalid CPU metrics."""
    invalid_data = {
        "physical_cores": "invalid",  # Should be int
        "logical_cores": -1,  # Should be positive
        "cpu_freq_current": None,  # Required
        "cpu_freq_min": "invalid",  # Should be float
        "cpu_freq_max": -1.0,  # Should be positive
        "cpu_percent": 101.0,  # Should be 0-100
        "per_cpu_percent": "invalid",  # Should be list
        "ctx_switches": -1,  # Should be positive
        "interrupts": None,  # Required
        "soft_interrupts": "invalid",  # Should be int
        "syscalls": -1,  # Should be positive
    }
    with pytest.raises(ValidationError):
        CPUMetrics(**invalid_data)


def test_memory_metrics_valid():
    """Test valid memory metrics."""
    metrics = MemoryMetrics(**VALID_MEMORY_DATA)
    assert metrics.total == MEM_TOTAL
    assert metrics.available == MEM_AVAILABLE
    assert metrics.used == MEM_USED
    assert metrics.free == MEM_FREE
    assert metrics.percent == MEM_PERCENT
    assert metrics.swap_total == MEM_SWAP_TOTAL
    assert metrics.swap_used == MEM_SWAP_USED
    assert metrics.swap_free == MEM_SWAP_FREE
    assert metrics.swap_percent == MEM_SWAP_PERCENT
    assert metrics.swap_in == MEM_SWAP_IN
    assert metrics.swap_out == MEM_SWAP_OUT


def test_memory_metrics_invalid():
    """Test invalid memory metrics."""
    invalid_data = {
        "total": "invalid",  # Should be int
        "available": -1,  # Should be positive
        "used": None,  # Required
        "free": "invalid",  # Should be int
        "percent": 101.0,  # Should be 0-100
        "swap_total": -1,  # Should be positive
        "swap_used": None,  # Required
        "swap_free": "invalid",  # Should be int
        "swap_percent": -1.0,  # Should be 0-100
        "swap_in": None,  # Required
        "swap_out": "invalid",  # Should be int
    }
    with pytest.raises(ValidationError):
        MemoryMetrics(**invalid_data)


def test_gpu_metrics_valid():
    """Test valid GPU metrics."""
    metrics = GPUMetrics(**VALID_GPU_DATA)
    assert metrics.name == GPU_NAME
    assert metrics.temperature == GPU_TEMPERATURE
    assert metrics.power_watts == GPU_POWER_WATTS
    assert metrics.memory_total == GPU_MEMORY_TOTAL
    assert metrics.memory_used == GPU_MEMORY_USED
    assert metrics.memory_free == GPU_MEMORY_FREE
    assert metrics.gpu_utilization == GPU_UTILIZATION
    assert metrics.memory_utilization == GPU_MEMORY_UTILIZATION
    assert metrics.fan_speed == GPU_FAN_SPEED


def test_gpu_metrics_invalid():
    """Test invalid GPU metrics."""
    invalid_data = {
        "name": 123,  # Should be string
        "temperature": "invalid",  # Should be float
        "power_watts": None,  # Required
        "memory_total": -1,  # Should be positive
        "memory_used": "invalid",  # Should be int
        "memory_free": None,  # Required
        "gpu_utilization": 101.0,  # Should be 0-100
        "memory_utilization": -1.0,  # Should be 0-100
        "fan_speed": "invalid",  # Should be float
    }
    with pytest.raises(ValidationError):
        GPUMetrics(**invalid_data)


def test_system_metrics_valid():
    """Test valid system metrics."""
    metrics = SystemMetrics(
        cpu=CPUMetrics(**VALID_CPU_DATA),
        memory=MemoryMetrics(**VALID_MEMORY_DATA),
        gpu=GPUMetrics(**VALID_GPU_DATA),
    )
    assert isinstance(metrics.cpu, CPUMetrics)
    assert isinstance(metrics.memory, MemoryMetrics)
    assert isinstance(metrics.gpu, GPUMetrics)


def test_system_metrics_invalid():
    """Test invalid system metrics."""
    invalid_data = {
        "cpu": {},  # Missing required fields
        "memory": None,  # Required
        "gpu": "invalid",  # Should be dict
    }
    with pytest.raises(ValidationError):
        SystemMetrics(**invalid_data)


def test_health_status_valid() -> None:
    """Test valid health status."""
    data = {
        "status": "healthy",
        "version": __version__,
        "system": {
            "api": "running",
            "collectors": "ready",
        },
    }
    status = HealthStatus(**data)
    assert status.status == "healthy"
    assert status.version == __version__
    assert status.system["api"] == "running"


def test_error_response_valid() -> None:
    """Test valid error response."""
    response = ErrorResponse(detail="Test error")
    assert response.detail == "Test error"


def test_metrics_response_valid(
    valid_cpu_metrics: dict[str, Any],
    valid_memory_metrics: dict[str, Any],
    valid_gpu_metrics: dict[str, Any],
) -> None:
    """Test valid metrics response.

    Args:
        valid_cpu_metrics: Valid CPU metrics data.
        valid_memory_metrics: Valid memory metrics data.
        valid_gpu_metrics: Valid GPU metrics data.
    """
    response = MetricsResponse(
        metrics={
            "cpu": CPUMetrics(**valid_cpu_metrics),
            "memory": MemoryMetrics(**valid_memory_metrics),
            "gpu": GPUMetrics(**valid_gpu_metrics),
        }
    )
    assert isinstance(response.metrics["cpu"], CPUMetrics)
    assert isinstance(response.metrics["memory"], MemoryMetrics)
    assert isinstance(response.metrics["gpu"], GPUMetrics)
