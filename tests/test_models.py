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

# Test constants
CPU_PHYSICAL_COUNT = 4
CPU_LOGICAL_COUNT = 8
CPU_FREQUENCY_MHZ = 2400.0
CPU_CTX_SWITCHES = 1000

MEMORY_TOTAL_BYTES = 16_000_000_000
MEMORY_VIRTUAL_PERCENT = 43.75
MEMORY_SWAP_TOTAL_BYTES = 8_000_000_000
MEMORY_SWAP_PERCENT = 12.5


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
            "current": CPU_FREQUENCY_MHZ,
            "min": CPU_FREQUENCY_MHZ,
            "max": CPU_FREQUENCY_MHZ
        },
        "percent": {
            "total": 25.5,
            "per_cpu": [25.5] * CPU_PHYSICAL_COUNT
        },
        "stats": {
            "ctx_switches": CPU_CTX_SWITCHES,
            "interrupts": 500,
            "soft_interrupts": 250,
            "syscalls": 750
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
            "total": MEMORY_TOTAL_BYTES,
            "available": MEMORY_TOTAL_BYTES // 2,
            "used": MEMORY_TOTAL_BYTES // 2,
            "free": MEMORY_TOTAL_BYTES // 4,
            "percent": MEMORY_VIRTUAL_PERCENT
        },
        "swap": {
            "total": MEMORY_SWAP_TOTAL_BYTES,
            "used": MEMORY_SWAP_TOTAL_BYTES // 4,
            "free": MEMORY_SWAP_TOTAL_BYTES * 3 // 4,
            "percent": MEMORY_SWAP_PERCENT,
            "sin": 1000,
            "sout": 500
        }
    }


def test_cpu_metrics_valid(valid_cpu_metrics: dict[str, Any]) -> None:
    """Test CPUMetrics with valid data.

    Args:
        valid_cpu_metrics: Valid CPU metrics data.
    """
    metrics = CPUMetrics(**valid_cpu_metrics)
    assert metrics.count["physical"] == CPU_PHYSICAL_COUNT
    assert metrics.count["logical"] == CPU_LOGICAL_COUNT
    assert metrics.frequency["current"] == CPU_FREQUENCY_MHZ
    assert len(metrics.percent["per_cpu"]) == CPU_PHYSICAL_COUNT
    assert metrics.stats["ctx_switches"] == CPU_CTX_SWITCHES


def test_cpu_metrics_invalid() -> None:
    """Test CPUMetrics with invalid data."""
    invalid_data = {
        "count": {
            "physical": "invalid",  # Should be int
            "logical": 8
        },
        "frequency": {
            "current": 2400.0
        },
        "percent": {
            "total": "25.5"  # Should be float
        },
        "stats": {}  # Missing required fields
    }
    
    with pytest.raises(ValidationError):
        CPUMetrics(**invalid_data)


def test_memory_metrics_valid(valid_memory_metrics: dict[str, Any]) -> None:
    """Test MemoryMetrics with valid data.

    Args:
        valid_memory_metrics: Valid memory metrics data.
    """
    metrics = MemoryMetrics(**valid_memory_metrics)
    assert metrics.virtual["total"] == MEMORY_TOTAL_BYTES
    assert metrics.virtual["percent"] == MEMORY_VIRTUAL_PERCENT
    assert metrics.swap["total"] == MEMORY_SWAP_TOTAL_BYTES
    assert metrics.swap["percent"] == MEMORY_SWAP_PERCENT


def test_memory_metrics_invalid() -> None:
    """Test MemoryMetrics with invalid data."""
    invalid_data = {
        "virtual": {
            "total": "invalid",  # Should be int
            "percent": 101.0  # Invalid percentage
        },
        "swap": {
            "used": -1  # Invalid negative value
        }
    }
    
    with pytest.raises(ValidationError):
        MemoryMetrics(**invalid_data)


def test_system_metrics_valid(
    valid_cpu_metrics: dict[str, Any],
    valid_memory_metrics: dict[str, Any]
) -> None:
    """Test SystemMetrics with valid data.

    Args:
        valid_cpu_metrics: Valid CPU metrics data.
        valid_memory_metrics: Valid memory metrics data.
    """
    metrics = SystemMetrics(
        cpu=CPUMetrics(**valid_cpu_metrics),
        memory=MemoryMetrics(**valid_memory_metrics)
    )
    assert isinstance(metrics.cpu, CPUMetrics)
    assert isinstance(metrics.memory, MemoryMetrics)


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