"""Tests for the metrics module."""

import re
from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.metrics.prometheus import (
    get_collector,
    get_latest_metrics,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class AsyncMock:
    """Helper class to create async mock objects."""

    def __init__(self, return_value):
        """Initialize with return value."""
        self.return_value = return_value

    async def __call__(self, *args, **kwargs):
        """Async call that returns the stored value."""
        return self.return_value


# Test constants
MEMORY_VIRTUAL_TOTAL = 16_000_000_000


@pytest.mark.asyncio
async def test_get_latest_metrics(mocker: "MockerFixture") -> None:
    """Test that get_latest_metrics returns Prometheus formatted metrics."""
    # Get collector instance
    collector = get_collector()
    
    # Mock the collect methods
    cpu_metrics = {
        "count": {"physical": 4, "logical": 8},
        "frequency": {"current": 2400.0, "min": 2200.0, "max": 3200.0},
        "percent": {"total": 25.5, "per_cpu": [20.0, 30.0, 25.0, 27.0]},
        "stats": {
            "ctx_switches": 1000,
            "interrupts": 500,
            "soft_interrupts": 200,
            "syscalls": 300
        }
    }
    memory_metrics = {
        "virtual": {
            "total": MEMORY_VIRTUAL_TOTAL,
            "available": 8_000_000_000,
            "used": 8_000_000_000,
            "free": 8_000_000_000,
            "percent": 50.0
        },
        "swap": {
            "total": 8_000_000_000,
            "used": 1_000_000_000,
            "free": 7_000_000_000,
            "percent": 12.5,
            "sin": 100,
            "sout": 50
        }
    }
    gpu_metrics = {
        "device_count": 0,
        "devices": []
    }
    
    # Mock collector methods
    mocker.patch.object(
        collector.cpu_collector,
        "collect",
        new=AsyncMock(cpu_metrics)
    )
    mocker.patch.object(
        collector.memory_collector,
        "collect",
        new=AsyncMock(memory_metrics)
    )
    mocker.patch.object(
        collector.gpu_collector,
        "collect_metrics",
        return_value=gpu_metrics
    )

    # Get metrics in Prometheus format
    metrics_bytes = await get_latest_metrics()
    metrics_text = metrics_bytes.decode("utf-8")

    # Verify metrics format
    assert isinstance(metrics_bytes, bytes)
    
    # CPU metrics - check for presence and values
    assert "# HELP cpu_physical_count" in metrics_text
    assert "# TYPE cpu_physical_count gauge" in metrics_text
    assert "cpu_physical_count 4.0" in metrics_text
    
    # Memory metrics - check for presence and values
    assert "# HELP memory_virtual_total_bytes" in metrics_text
    assert "# TYPE memory_virtual_total_bytes gauge" in metrics_text
    
    pattern = r"memory_virtual_total_bytes\s+([\d.e+-]+)"
    memory_virtual_match = re.search(pattern, metrics_text)
    assert memory_virtual_match is not None, (
        "memory_virtual_total_bytes metric not found"
    )
    assert float(memory_virtual_match.group(1)) == float(MEMORY_VIRTUAL_TOTAL)
