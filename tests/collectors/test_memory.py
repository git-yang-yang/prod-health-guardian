"""Tests for the memory collector."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors.memory import MemoryCollector
from tests.collectors.conftest import (
    FREE_MEMORY,
    FREE_SWAP,
    MEMORY_PERCENT,
    SWAP_IN,
    SWAP_OUT,
    SWAP_PERCENT,
    TOTAL_MEMORY,
    TOTAL_SWAP,
    USED_MEMORY,
    USED_SWAP,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_memory_collector_init() -> None:
    """Test memory collector initialization."""
    collector = MemoryCollector()
    assert collector.get_name() == "memory"
    assert collector.interval == 1.0


@pytest.mark.asyncio
async def test_memory_collector_metrics(mock_memory_psutil: "MockerFixture") -> None:
    """Test memory collector metrics collection.

    Args:
        mock_memory_psutil: Mocked psutil fixture.
    """
    collector = MemoryCollector()
    metrics = await collector.collect()

    # Validate metric structure
    assert isinstance(metrics, dict)
    assert all(isinstance(key, str) for key in metrics.keys())
    assert all(isinstance(value, (int, float)) for value in metrics.values())

    # Validate virtual memory metrics
    assert metrics["total"] == TOTAL_MEMORY  # 16GB
    assert metrics["used"] == USED_MEMORY  # 8GB
    assert metrics["free"] == FREE_MEMORY  # 8GB
    assert metrics["available"] == FREE_MEMORY  # 8GB
    assert metrics["percent"] == MEMORY_PERCENT

    # Validate swap memory metrics
    assert metrics["swap_total"] == TOTAL_SWAP  # 8GB
    assert metrics["swap_used"] == USED_SWAP  # 1GB
    assert metrics["swap_free"] == FREE_SWAP  # 7GB
    assert metrics["swap_percent"] == SWAP_PERCENT
    assert metrics["swap_in"] == SWAP_IN
    assert metrics["swap_out"] == SWAP_OUT


@pytest.mark.asyncio
async def test_memory_collector_no_swap(mock_memory_psutil: "MockerFixture") -> None:
    """Test memory collector when swap memory is not available.

    Args:
        mock_memory_psutil: Mocked psutil fixture.
    """
    # Mock swap_memory to raise an exception
    mock_memory_psutil.swap_memory.side_effect = AttributeError(
        "No swap memory available"
    )

    collector = MemoryCollector()
    metrics = await collector.collect()

    # Virtual memory metrics should still be available
    assert metrics["total"] == TOTAL_MEMORY
    assert metrics["used"] == USED_MEMORY
    assert metrics["free"] == FREE_MEMORY
    assert metrics["available"] == FREE_MEMORY
    assert metrics["percent"] == MEMORY_PERCENT

    # Swap memory metrics should be 0
    assert metrics["swap_total"] == 0
    assert metrics["swap_used"] == 0
    assert metrics["swap_free"] == 0
    assert metrics["swap_percent"] == 0.0
    assert metrics["swap_in"] == 0
    assert metrics["swap_out"] == 0
