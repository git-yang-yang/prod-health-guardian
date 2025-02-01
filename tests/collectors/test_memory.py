"""Tests for memory metrics collector."""

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from prod_health_guardian.collectors.memory import MemoryCollector

if TYPE_CHECKING:
    pass  # No unused imports

# Test constants
TOTAL_MEMORY = 16_000_000_000  # 16GB
USED_MEMORY = 8_000_000_000  # 8GB
FREE_MEMORY = 8_000_000_000  # 8GB
MEMORY_PERCENT = 50.0

TOTAL_SWAP = 8_000_000_000  # 8GB
USED_SWAP = 1_000_000_000  # 1GB
FREE_SWAP = 7_000_000_000  # 7GB
SWAP_PERCENT = 12.5
SWAP_IN = 100
SWAP_OUT = 50


@pytest.fixture
def mock_psutil(mocker: MockerFixture) -> MockerFixture:
    """Mock psutil for consistent testing.

    Args:
        mocker: Pytest mocker fixture.

    Returns:
        MockerFixture: Configured mocker.
    """
    mock = mocker.patch("prod_health_guardian.collectors.memory.psutil")

    # Set up virtual memory mock
    mock.virtual_memory.return_value.total = TOTAL_MEMORY
    mock.virtual_memory.return_value.used = USED_MEMORY
    mock.virtual_memory.return_value.free = FREE_MEMORY
    mock.virtual_memory.return_value.available = FREE_MEMORY
    mock.virtual_memory.return_value.percent = MEMORY_PERCENT

    # Set up swap memory mock
    mock.swap_memory.return_value.total = TOTAL_SWAP
    mock.swap_memory.return_value.used = USED_SWAP
    mock.swap_memory.return_value.free = FREE_SWAP
    mock.swap_memory.return_value.percent = SWAP_PERCENT
    mock.swap_memory.return_value.sin = SWAP_IN
    mock.swap_memory.return_value.sout = SWAP_OUT

    return mock


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_memory_collector_name() -> None:
    """Test memory collector name."""
    collector = MemoryCollector()
    assert collector.get_name() == "memory"


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_memory_collector_metrics(mock_psutil: MockerFixture) -> None:
    """Test memory metrics collection with mocked psutil.

    Args:
        mock_psutil: Mocked psutil module.
    """
    collector = MemoryCollector()
    metrics = await collector.collect()

    # Check structure
    assert "virtual" in metrics
    assert "swap" in metrics

    # Check virtual memory metrics
    virtual = metrics["virtual"]
    assert isinstance(virtual["total"], int)
    assert isinstance(virtual["available"], int)
    assert isinstance(virtual["used"], int)
    assert isinstance(virtual["free"], int)
    assert isinstance(virtual["percent"], float)

    assert virtual["total"] == TOTAL_MEMORY
    assert virtual["used"] == USED_MEMORY
    assert virtual["free"] == FREE_MEMORY
    assert virtual["available"] == FREE_MEMORY
    assert virtual["percent"] == MEMORY_PERCENT

    # Check swap memory metrics
    swap = metrics["swap"]
    assert isinstance(swap["total"], int)
    assert isinstance(swap["used"], int)
    assert isinstance(swap["free"], int)
    assert isinstance(swap["percent"], float)
    assert isinstance(swap["sin"], int)
    assert isinstance(swap["sout"], int)

    assert swap["total"] == TOTAL_SWAP
    assert swap["used"] == USED_SWAP
    assert swap["free"] == FREE_SWAP
    assert swap["percent"] == SWAP_PERCENT
    assert swap["sin"] == SWAP_IN
    assert swap["sout"] == SWAP_OUT


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_memory_collector_no_swap(mock_psutil: MockerFixture) -> None:
    """Test memory metrics collection when swap is not available.

    Args:
        mock_psutil: Mocked psutil module.
    """
    # Mock swap_memory to raise an error
    mock_psutil.swap_memory.side_effect = Exception("No swap memory")

    collector = MemoryCollector()
    metrics = await collector.collect()

    # Virtual memory should still be available
    assert "virtual" in metrics
    assert metrics["virtual"]["total"] == TOTAL_MEMORY

    # Swap metrics should be zeros
    swap = metrics["swap"]
    assert swap["total"] == 0
    assert swap["used"] == 0
    assert swap["free"] == 0
    assert swap["percent"] == 0.0
    assert swap["sin"] == 0
    assert swap["sout"] == 0
