"""Tests for the metrics module."""

from typing import TYPE_CHECKING

from prod_health_guardian.metrics.prometheus import (
    get_latest_metrics,
    update_cpu_metrics,
    update_memory_metrics,
)

# Remove unused imports
if TYPE_CHECKING:
    pass  # Keep TYPE_CHECKING for future use


def test_get_latest_metrics() -> None:
    """Test that get_latest_metrics returns Prometheus formatted metrics."""
    # Update some test metrics
    cpu_metrics = {
        "count": {"physical": 4, "logical": 8},
        "frequency": {"current": 2400.0, "min": 2200.0, "max": 3200.0},
        "percent": {"total": 25.5, "per_cpu": [20.0, 30.0, 25.0, 27.0]},
        "stats": {
            "ctx_switches": 1000,
            "interrupts": 500,
            "soft_interrupts": 200,
            "syscalls": 5000
        }
    }
    memory_metrics = {
        "virtual": {
            "total": 16_000_000_000,
            "available": 8_000_000_000,
            "used": 7_000_000_000,
            "free": 1_000_000_000,
            "percent": 43.75
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

    update_cpu_metrics(cpu_metrics)
    update_memory_metrics(memory_metrics)

    # Get the metrics in Prometheus format
    metrics = get_latest_metrics()
    assert isinstance(metrics, bytes)
    assert len(metrics) > 0

    # Convert to string for basic content checks
    metrics_str = metrics.decode("utf-8")
    
    # Check CPU metrics
    assert "cpu_physical_count 4.0" in metrics_str
    assert "cpu_logical_count 8.0" in metrics_str
    assert "cpu_frequency_current_mhz 2400.0" in metrics_str
    assert "cpu_percent_total 25.5" in metrics_str
    assert "cpu_ctx_switches_total 1000.0" in metrics_str
    
    # Check memory metrics
    assert "memory_virtual_total_bytes" in metrics_str
    assert "memory_swap_total_bytes" in metrics_str
