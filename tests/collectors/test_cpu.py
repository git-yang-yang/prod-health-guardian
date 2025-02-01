"""Tests for the CPU collector."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors.cpu import CPUCollector
from tests.collectors.conftest import (
    CPU_CTX_SWITCHES,
    CPU_FREQ_CURRENT,
    CPU_FREQ_MAX,
    CPU_FREQ_MIN,
    CPU_INTERRUPTS,
    CPU_LOGICAL_CORES,
    CPU_PER_CPU_PERCENT,
    CPU_PHYSICAL_CORES,
    CPU_SOFT_INTERRUPTS,
    CPU_SYSCALLS,
    CPU_TOTAL_PERCENT,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_cpu_collector_init() -> None:
    """Test CPU collector initialization."""
    collector = CPUCollector()
    assert collector.get_name() == "cpu"
    assert collector.interval == 1.0


@pytest.mark.asyncio
async def test_cpu_collector_metrics(mock_cpu_psutil: "MockerFixture") -> None:
    """Test CPU collector metrics collection.

    Args:
        mock_cpu_psutil: Mocked psutil fixture.
    """
    collector = CPUCollector()
    metrics = await collector.collect()

    # Validate metric structure
    assert isinstance(metrics, dict)
    assert all(isinstance(key, str) for key in metrics.keys())
    assert all(isinstance(value, (int, float, list)) for value in metrics.values())

    # Validate core counts
    assert metrics["physical_cores"] == CPU_PHYSICAL_CORES
    assert metrics["logical_cores"] == CPU_LOGICAL_CORES

    # Validate CPU frequency
    assert metrics["cpu_freq_current"] == CPU_FREQ_CURRENT
    assert metrics["cpu_freq_min"] == CPU_FREQ_MIN
    assert metrics["cpu_freq_max"] == CPU_FREQ_MAX

    # Validate CPU percentages
    assert metrics["cpu_percent"] == CPU_TOTAL_PERCENT
    assert metrics["per_cpu_percent"] == CPU_PER_CPU_PERCENT

    # Validate CPU stats
    assert metrics["ctx_switches"] == CPU_CTX_SWITCHES
    assert metrics["interrupts"] == CPU_INTERRUPTS
    assert metrics["soft_interrupts"] == CPU_SOFT_INTERRUPTS
    assert metrics["syscalls"] == CPU_SYSCALLS


@pytest.mark.asyncio
async def test_cpu_collector_no_frequency(mock_cpu_psutil: "MockerFixture") -> None:
    """Test CPU collector when frequency information is not available.

    Args:
        mock_cpu_psutil: Mocked psutil fixture.
    """
    # Mock CPU frequency as None
    mock_cpu_psutil.cpu_freq.return_value = None

    collector = CPUCollector()
    metrics = await collector.collect()

    # Frequency metrics should be 0.0 when not available
    assert metrics["cpu_freq_current"] == 0.0
    assert metrics["cpu_freq_min"] == 0.0
    assert metrics["cpu_freq_max"] == 0.0

    # Other metrics should still be available
    assert metrics["physical_cores"] == CPU_PHYSICAL_CORES
    assert metrics["logical_cores"] == CPU_LOGICAL_CORES
    assert metrics["cpu_percent"] == CPU_TOTAL_PERCENT
