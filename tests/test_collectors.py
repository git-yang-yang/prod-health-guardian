"""Tests for hardware metric collectors."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors.cpu import CPUCollector
from prod_health_guardian.collectors.memory import MemoryCollector

if TYPE_CHECKING:
    pass  # No type-only imports needed

# Constants
MIN_PERCENT = 0
MAX_PERCENT = 100


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_cpu_collector() -> None:
    """Test CPU metrics collection."""
    collector = CPUCollector(interval=0.1)  # Short interval for testing
    assert collector.get_name() == "cpu"

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


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_memory_collector() -> None:
    """Test memory metrics collection."""
    collector = MemoryCollector()
    assert collector.get_name() == "memory"

    metrics = await collector.collect()
    
    # Check structure
    assert "virtual" in metrics
    assert "swap" in metrics

    # Check virtual memory metrics
    virtual = metrics["virtual"]
    expected_keys = ["total", "available", "used", "free", "percent"]
    assert all(key in virtual for key in expected_keys)
    assert isinstance(virtual["total"], int)
    assert isinstance(virtual["percent"], float)
    assert MIN_PERCENT <= virtual["percent"] <= MAX_PERCENT

    # Check swap memory metrics
    swap = metrics["swap"]
    assert all(key in swap for key in ["total", "used", "free", "percent"])
    assert isinstance(swap["total"], int)
    assert isinstance(swap["percent"], float)
    assert MIN_PERCENT <= swap["percent"] <= MAX_PERCENT 