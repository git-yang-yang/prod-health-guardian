"""Tests for the metrics module."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.metrics.prometheus import (
    get_collector,
    get_latest_metrics,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

# Test constants
MEMORY_VIRTUAL_TOTAL = 16_000_000_000.0


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
            "available": 8000000000,
            "used": 8000000000,
            "free": 8000000000,
            "percent": 50.0
        },
        "swap": {
            "total": 8000000000,
            "used": 1000000000,
            "free": 7000000000,
            "percent": 12.5,
            "sin": 100,
            "sout": 50
        }
    }
    
    # Mock collector methods
    mocker.patch.object(
        collector.cpu_collector,
        "collect",
        return_value=cpu_metrics
    )
    mocker.patch.object(
        collector.memory_collector,
        "collect",
        return_value=memory_metrics
    )

    # Get metrics in Prometheus format
    metrics_bytes = await get_latest_metrics()
    metrics_text = metrics_bytes.decode("utf-8")

    # Verify metrics format
    assert isinstance(metrics_bytes, bytes)
    
    # CPU metrics - check for presence and values
    assert "# HELP cpu_physical_count" in metrics_text
    assert "# TYPE cpu_physical_count gauge" in metrics_text
    assert "cpu_physical_count 4" in metrics_text.replace(".0", "")
    
    # Memory metrics - check for presence and values
    assert "# HELP memory_virtual_total_bytes" in metrics_text
    assert "# TYPE memory_virtual_total_bytes gauge" in metrics_text
    
    # Find the actual memory metric line
    for line in metrics_text.split("\n"):
        if line.startswith("memory_virtual_total_bytes"):
            assert float(line.split()[1]) == MEMORY_VIRTUAL_TOTAL
            break
    else:
        raise AssertionError("memory_virtual_total_bytes metric not found")
