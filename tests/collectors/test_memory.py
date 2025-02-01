"""Tests for Memory metrics collector."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors.memory import MemoryCollector

if TYPE_CHECKING:
    pass  # No unused imports

# Test constants
MIN_PERCENT = 0
MAX_PERCENT = 100


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_memory_collector_name() -> None:
    """Test memory collector name."""
    collector = MemoryCollector()
    assert collector.get_name() == "memory"


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_memory_collector_metrics() -> None:
    """Test memory metrics collection."""
    collector = MemoryCollector()
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
