"""Test metrics collection and formatting."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.metrics import get_collector
from tests.conftest import MEMORY_VIRTUAL_TOTAL
from tests.utils import AsyncMock

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


@pytest.mark.asyncio
async def test_get_latest_metrics(mocker: "MockerFixture") -> None:
    """Test that get_latest_metrics returns Prometheus formatted metrics."""
    # Get collector instance
    collector = get_collector()

    # Mock the collect methods
    cpu_metrics = {
        "physical_cores": 4,
        "logical_cores": 8,
        "cpu_freq_current": 2400.0,
        "cpu_freq_min": 2200.0,
        "cpu_freq_max": 3200.0,
        "cpu_percent": 25.5,
        "per_cpu_percent": [20.0, 30.0, 25.0, 27.0],
        "ctx_switches": 1000,
        "interrupts": 500,
        "soft_interrupts": 200,
        "syscalls": 300,
    }
    memory_metrics = {
        "total": MEMORY_VIRTUAL_TOTAL,
        "available": 8_000_000_000,
        "used": 8_000_000_000,
        "free": 8_000_000_000,
        "percent": 50.0,
        "swap_total": 8_000_000_000,
        "swap_used": 1_000_000_000,
        "swap_free": 7_000_000_000,
        "swap_percent": 12.5,
        "swap_in": 100,
        "swap_out": 50,
    }
    gpu_metrics = {
        "name": "No GPU",
        "temperature": 0.0,
        "power_watts": 0.0,
        "memory_total": 0,
        "memory_used": 0,
        "memory_free": 0,
        "gpu_utilization": 0.0,
        "memory_utilization": 0.0,
        "fan_speed": 0.0,
    }

    # Mock collector methods
    mocker.patch.object(
        collector.cpu_collector,
        "collect",
        new=AsyncMock(return_value=cpu_metrics),
    )
    mocker.patch.object(
        collector.memory_collector,
        "collect",
        new=AsyncMock(return_value=memory_metrics),
    )
    mocker.patch.object(
        collector.gpu_collector,
        "collect",
        new=AsyncMock(return_value=gpu_metrics),
    )

    # Get metrics
    metrics = await collector.get_latest_metrics()

    # Validate metrics format
    assert isinstance(metrics, str)
    assert "HELP" in metrics
    assert "TYPE" in metrics

    # Validate CPU metrics
    assert "cpu_physical_count" in metrics
    assert "cpu_logical_count" in metrics
    assert "cpu_frequency_current_mhz" in metrics
    assert "cpu_frequency_min_mhz" in metrics
    assert "cpu_frequency_max_mhz" in metrics
    assert "cpu_percent_total" in metrics
    assert "cpu_percent_per_cpu" in metrics
    assert "cpu_ctx_switches_total" in metrics
    assert "cpu_interrupts_total" in metrics
    assert "cpu_soft_interrupts_total" in metrics
    assert "cpu_syscalls_total" in metrics

    # Validate memory metrics
    assert "memory_virtual_total_bytes" in metrics
    assert "memory_virtual_available_bytes" in metrics
    assert "memory_virtual_used_bytes" in metrics
    assert "memory_virtual_free_bytes" in metrics
    assert "memory_virtual_percent" in metrics
    assert "memory_swap_total_bytes" in metrics
    assert "memory_swap_used_bytes" in metrics
    assert "memory_swap_free_bytes" in metrics
    assert "memory_swap_percent" in metrics
    assert "memory_swap_sin_total" in metrics
    assert "memory_swap_sout_total" in metrics

    # Validate GPU metrics
    assert "gpu_temperature_celsius" in metrics
    assert "gpu_power_watts" in metrics
    assert "gpu_memory_total_bytes" in metrics
    assert "gpu_memory_used_bytes" in metrics
    assert "gpu_memory_free_bytes" in metrics
    assert "gpu_utilization_percent" in metrics
    assert "gpu_memory_utilization_percent" in metrics
    assert "gpu_fan_speed_percent" in metrics
