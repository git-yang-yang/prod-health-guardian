"""Tests for CPU metrics collector."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors.cpu import CPUCollector

if TYPE_CHECKING:
    pass  # No unused imports

# Test constants
MIN_PERCENT = 0
MAX_PERCENT = 100


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_cpu_collector_name() -> None:
    """Test CPU collector name."""
    collector = CPUCollector()
    assert collector.get_name() == "cpu"


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_cpu_collector_metrics() -> None:
    """Test CPU metrics collection."""
    collector = CPUCollector(interval=0.1)  # Short interval for testing
    metrics = await collector.collect()
    
    # Check structure
    assert "count" in metrics
    assert "frequency" in metrics
    assert "percent" in metrics
    assert "stats" in metrics

    # Check CPU count
    count = metrics["count"]
    assert isinstance(count["physical"], int)
    assert isinstance(count["logical"], int)
    assert count["logical"] >= count["physical"]

    # Check CPU frequency
    freq = metrics["frequency"]
    if freq["current"] is not None:  # Some systems might not report frequency
        assert isinstance(freq["current"], float)
        if freq["min"] is not None:
            assert isinstance(freq["min"], float)
        if freq["max"] is not None:
            assert isinstance(freq["max"], float)

    # Check CPU percentage
    percent = metrics["percent"]
    assert isinstance(percent["total"], float)
    assert MIN_PERCENT <= percent["total"] <= MAX_PERCENT
    assert isinstance(percent["per_cpu"], list)
    assert all(MIN_PERCENT <= x <= MAX_PERCENT for x in percent["per_cpu"])

    # Check CPU stats
    stats = metrics["stats"]
    assert isinstance(stats["ctx_switches"], int)
    assert isinstance(stats["interrupts"], int)
    assert isinstance(stats["soft_interrupts"], int)
    assert isinstance(stats["syscalls"], int) 