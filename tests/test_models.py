"""Tests for data models."""

from typing import Any

import pytest
from pydantic import ValidationError

from prod_health_guardian import __version__
from prod_health_guardian.models import (
    CPUMetrics,
    ErrorResponse,
    HealthStatus,
    MemoryMetrics,
    MetricsResponse,
    SystemMetrics,
)
from prod_health_guardian.models.metrics import (
    GPUDeviceMetrics,
    GPUMetrics,
)

# Test constants
CPU_PHYSICAL_COUNT = 4
CPU_LOGICAL_COUNT = 8
CPU_FREQ_CURRENT = 2400.0
CPU_FREQ_MIN = 2200.0
CPU_FREQ_MAX = 3200.0
CPU_PERCENT_TOTAL = 25.5
CPU_PERCENT_PER_CPU = [20.0, 30.0, 25.0, 27.0]
CPU_CTX_SWITCHES = 1000
CPU_INTERRUPTS = 500
CPU_SOFT_INTERRUPTS = 200
CPU_SYSCALLS = 300

# Memory test constants
MEM_VIRTUAL_TOTAL = 16_000_000_000
MEM_VIRTUAL_AVAILABLE = 8_000_000_000
MEM_VIRTUAL_USED = 8_000_000_000
MEM_VIRTUAL_FREE = 8_000_000_000
MEM_VIRTUAL_PERCENT = 50.0
MEM_SWAP_TOTAL = 8_000_000_000
MEM_SWAP_USED = 1_000_000_000
MEM_SWAP_FREE = 7_000_000_000
MEM_SWAP_PERCENT = 12.5
MEM_SWAP_SIN = 100
MEM_SWAP_SOUT = 50

# GPU test constants
GPU_DEVICE_COUNT = 2
GPU_NAME = "NVIDIA GeForce RTX 3080"
GPU_TEMPERATURE = 65.0
GPU_POWER_WATTS = 220.5
GPU_MEMORY_TOTAL = 10_737_418_240  # 10GB
GPU_MEMORY_USED = 4_294_967_296    # 4GB
GPU_MEMORY_FREE = 6_442_450_944    # 6GB
GPU_UTILIZATION = 85.5
GPU_MEMORY_UTILIZATION = 40.0
GPU_FAN_SPEED = 75.0

# Test data
VALID_CPU_DATA = {
    "count": {
        "physical": CPU_PHYSICAL_COUNT,
        "logical": CPU_LOGICAL_COUNT
    },
    "frequency": {
        "current": CPU_FREQ_CURRENT,
        "min": CPU_FREQ_MIN,
        "max": CPU_FREQ_MAX
    },
    "percent": {
        "total": CPU_PERCENT_TOTAL,
        "per_cpu": CPU_PERCENT_PER_CPU
    },
    "stats": {
        "ctx_switches": CPU_CTX_SWITCHES,
        "interrupts": CPU_INTERRUPTS,
        "soft_interrupts": CPU_SOFT_INTERRUPTS,
        "syscalls": CPU_SYSCALLS
    }
}

VALID_MEMORY_DATA = {
    "virtual": {
        "total": MEM_VIRTUAL_TOTAL,
        "available": MEM_VIRTUAL_AVAILABLE,
        "used": MEM_VIRTUAL_USED,
        "free": MEM_VIRTUAL_FREE,
        "percent": MEM_VIRTUAL_PERCENT
    },
    "swap": {
        "total": MEM_SWAP_TOTAL,
        "used": MEM_SWAP_USED,
        "free": MEM_SWAP_FREE,
        "percent": MEM_SWAP_PERCENT,
        "sin": MEM_SWAP_SIN,
        "sout": MEM_SWAP_SOUT
    }
}

VALID_GPU_DEVICE_DATA = {
    "name": GPU_NAME,
    "temperature": GPU_TEMPERATURE,
    "power_usage": GPU_POWER_WATTS,
    "memory_total": GPU_MEMORY_TOTAL,
    "memory_used": GPU_MEMORY_USED,
    "memory_free": GPU_MEMORY_FREE,
    "utilization": GPU_UTILIZATION,
    "memory_utilization": GPU_MEMORY_UTILIZATION,
    "fan_speed": GPU_FAN_SPEED
}

VALID_GPU_DATA = {
    "device_count": GPU_DEVICE_COUNT,
    "devices": [VALID_GPU_DEVICE_DATA, VALID_GPU_DEVICE_DATA]
}


@pytest.fixture
def valid_cpu_metrics() -> dict[str, Any]:
    """Valid CPU metrics fixture.

    Returns:
        dict[str, Any]: Valid CPU metrics data.
    """
    return {
        "count": {
            "physical": CPU_PHYSICAL_COUNT,
            "logical": CPU_LOGICAL_COUNT
        },
        "frequency": {
            "current": CPU_FREQ_CURRENT,
            "min": CPU_FREQ_MIN,
            "max": CPU_FREQ_MAX
        },
        "percent": {
            "total": CPU_PERCENT_TOTAL,
            "per_cpu": CPU_PERCENT_PER_CPU
        },
        "stats": {
            "ctx_switches": CPU_CTX_SWITCHES,
            "interrupts": CPU_INTERRUPTS,
            "soft_interrupts": CPU_SOFT_INTERRUPTS,
            "syscalls": CPU_SYSCALLS
        }
    }


@pytest.fixture
def valid_memory_metrics() -> dict[str, Any]:
    """Valid memory metrics fixture.

    Returns:
        dict[str, Any]: Valid memory metrics data.
    """
    return {
        "virtual": {
            "total": MEM_VIRTUAL_TOTAL,
            "available": MEM_VIRTUAL_AVAILABLE,
            "used": MEM_VIRTUAL_USED,
            "free": MEM_VIRTUAL_FREE,
            "percent": MEM_VIRTUAL_PERCENT
        },
        "swap": {
            "total": MEM_SWAP_TOTAL,
            "used": MEM_SWAP_USED,
            "free": MEM_SWAP_FREE,
            "percent": MEM_SWAP_PERCENT,
            "sin": MEM_SWAP_SIN,
            "sout": MEM_SWAP_SOUT
        }
    }


def test_cpu_metrics_valid():
    """Test valid CPU metrics."""
    metrics = CPUMetrics(**VALID_CPU_DATA)
    assert metrics.count["physical"] == CPU_PHYSICAL_COUNT
    assert metrics.count["logical"] == CPU_LOGICAL_COUNT
    assert metrics.frequency["current"] == CPU_FREQ_CURRENT
    assert metrics.percent["total"] == CPU_PERCENT_TOTAL
    assert len(metrics.percent["per_cpu"]) == CPU_PHYSICAL_COUNT
    assert metrics.stats["ctx_switches"] == CPU_CTX_SWITCHES


def test_cpu_metrics_invalid():
    """Test invalid CPU metrics."""
    invalid_data = {
        "count": {"physical": "invalid"},  # Should be int
        "frequency": {"current": None},
        "percent": {"total": "invalid"},   # Should be float
        "stats": {}  # Missing required fields
    }
    with pytest.raises(ValidationError):
        CPUMetrics(**invalid_data)


def test_memory_metrics_valid():
    """Test valid memory metrics."""
    metrics = MemoryMetrics(**VALID_MEMORY_DATA)
    assert metrics.virtual["total"] == MEM_VIRTUAL_TOTAL
    assert metrics.virtual["percent"] == MEM_VIRTUAL_PERCENT
    assert metrics.swap["total"] == MEM_SWAP_TOTAL
    assert metrics.swap["percent"] == MEM_SWAP_PERCENT


def test_memory_metrics_invalid():
    """Test invalid memory metrics."""
    invalid_data = {
        "virtual": {"total": "invalid"},  # Should be int
        "swap": {}  # Missing required fields
    }
    with pytest.raises(ValidationError):
        MemoryMetrics(**invalid_data)


def test_gpu_device_metrics_valid():
    """Test valid GPU device metrics."""
    metrics = GPUDeviceMetrics(**VALID_GPU_DEVICE_DATA)
    assert metrics.name == GPU_NAME
    assert metrics.temperature == GPU_TEMPERATURE
    assert metrics.power_usage == GPU_POWER_WATTS
    assert metrics.memory_total == GPU_MEMORY_TOTAL
    assert metrics.memory_used == GPU_MEMORY_USED
    assert metrics.memory_free == GPU_MEMORY_FREE
    assert metrics.utilization == GPU_UTILIZATION
    assert metrics.memory_utilization == GPU_MEMORY_UTILIZATION
    assert metrics.fan_speed == GPU_FAN_SPEED


def test_gpu_device_metrics_invalid():
    """Test invalid GPU device metrics."""
    invalid_data = {
        "name": 123,  # Should be string
        "temperature": "invalid",  # Should be float
        "power_usage": None,  # Required
        "memory_total": -1,  # Should be positive
        "memory_used": "invalid",  # Should be int
        "memory_free": None,  # Required
        "utilization": 101.0,  # Should be 0-100
        "memory_utilization": -1.0,  # Should be positive
        "fan_speed": "invalid"  # Should be float
    }
    with pytest.raises(ValidationError):
        GPUDeviceMetrics(**invalid_data)


def test_gpu_metrics_valid():
    """Test valid GPU metrics."""
    metrics = GPUMetrics(**VALID_GPU_DATA)
    assert metrics.device_count == GPU_DEVICE_COUNT
    assert len(metrics.devices) == GPU_DEVICE_COUNT
    assert metrics.devices[0].name == GPU_NAME
    assert metrics.devices[1].temperature == GPU_TEMPERATURE


def test_gpu_metrics_invalid():
    """Test invalid GPU metrics."""
    invalid_data = {
        "device_count": -1,  # Should be non-negative
        "devices": "invalid"  # Should be list
    }
    with pytest.raises(ValidationError):
        GPUMetrics(**invalid_data)


def test_system_metrics_valid():
    """Test valid system metrics."""
    metrics = SystemMetrics(
        cpu=CPUMetrics(**VALID_CPU_DATA),
        memory=MemoryMetrics(**VALID_MEMORY_DATA),
        gpu=GPUMetrics(**VALID_GPU_DATA)
    )
    assert metrics.cpu.count["physical"] == CPU_PHYSICAL_COUNT
    assert metrics.memory.virtual["total"] == MEM_VIRTUAL_TOTAL
    assert metrics.gpu.device_count == GPU_DEVICE_COUNT


def test_system_metrics_invalid():
    """Test invalid system metrics."""
    with pytest.raises(ValidationError):
        SystemMetrics(
            cpu="invalid",  # Should be CPUMetrics
            memory="invalid",  # Should be MemoryMetrics
            gpu="invalid"  # Should be GPUMetrics
        )


def test_health_status_valid() -> None:
    """Test HealthStatus with valid data."""
    status = HealthStatus(
        status="healthy",
        version=__version__,
        system={
            "api": "running",
            "collectors": "ready"
        }
    )
    assert status.status == "healthy"
    assert status.version == __version__
    assert status.system["api"] == "running"


def test_error_response_valid() -> None:
    """Test ErrorResponse with valid data."""
    error = ErrorResponse(
        detail="Test error message"
    )
    assert error.detail == "Test error message"


def test_metrics_response_valid(
    valid_cpu_metrics: dict[str, Any],
    valid_memory_metrics: dict[str, Any]
) -> None:
    """Test MetricsResponse with valid data.

    Args:
        valid_cpu_metrics: Valid CPU metrics data.
        valid_memory_metrics: Valid memory metrics data.
    """
    response = MetricsResponse(metrics={
        "cpu": valid_cpu_metrics,
        "memory": valid_memory_metrics
    })
    assert isinstance(response.metrics, dict)
    assert "cpu" in response.metrics
    assert "memory" in response.metrics 