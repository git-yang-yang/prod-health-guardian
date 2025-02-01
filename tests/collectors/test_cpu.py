"""Tests for CPU metrics collector."""

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from prod_health_guardian.collectors.cpu import CPUCollector

if TYPE_CHECKING:
    pass  # No unused imports

# Test constants
MIN_PERCENT = 0
MAX_PERCENT = 100
TEST_INTERVAL = 0.1
DEFAULT_INTERVAL = 0.1
CUSTOM_INTERVAL = 0.5

# CPU count constants
PHYSICAL_CORES = 4
LOGICAL_CORES = 8

# CPU frequency constants (MHz)
CURRENT_FREQ = 3700.0
MIN_FREQ = 2200.0
MAX_FREQ = 4500.0

# CPU usage constants
TOTAL_CPU_PERCENT = 25.5
PER_CPU_PERCENT = [20.0, 30.0, 25.0, 27.0]

# CPU stats constants
CTX_SWITCHES = 1000
INTERRUPTS = 500
SOFT_INTERRUPTS = 200
SYSCALLS = 300


def get_cpu_count(logical: bool) -> int:
    """Get CPU count based on logical flag.

    Args:
        logical: Whether to return logical or physical core count.

    Returns:
        int: Number of CPU cores.
    """
    return LOGICAL_CORES if logical else PHYSICAL_CORES


@pytest.fixture
def mock_psutil(mocker: MockerFixture) -> MockerFixture:
    """Mock psutil for consistent testing.

    Args:
        mocker: Pytest mocker fixture.

    Returns:
        MockerFixture: Configured mocker.
    """
    mock = mocker.patch("prod_health_guardian.collectors.cpu.psutil")

    # Set up mock values
    mock.cpu_count.side_effect = get_cpu_count
    mock.cpu_freq.return_value.current = CURRENT_FREQ
    mock.cpu_freq.return_value.min = MIN_FREQ
    mock.cpu_freq.return_value.max = MAX_FREQ
    mock.cpu_percent.return_value = TOTAL_CPU_PERCENT
    mock.cpu_percent.side_effect = (
        lambda interval, percpu=False: PER_CPU_PERCENT if percpu else TOTAL_CPU_PERCENT
    )
    mock.cpu_stats.return_value.ctx_switches = CTX_SWITCHES
    mock.cpu_stats.return_value.interrupts = INTERRUPTS
    mock.cpu_stats.return_value.soft_interrupts = SOFT_INTERRUPTS
    mock.cpu_stats.return_value.syscalls = SYSCALLS

    return mock


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_cpu_collector_name() -> None:
    """Test CPU collector name."""
    collector = CPUCollector()
    assert collector.get_name() == "cpu"


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_cpu_collector_init() -> None:
    """Test CPU collector initialization."""
    # Test default interval
    collector = CPUCollector()
    assert collector.interval == DEFAULT_INTERVAL

    # Test custom interval
    collector = CPUCollector(interval=CUSTOM_INTERVAL)
    assert collector.interval == CUSTOM_INTERVAL


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_cpu_collector_metrics(mock_psutil: MockerFixture) -> None:
    """Test CPU metrics collection with mocked psutil.

    Args:
        mock_psutil: Mocked psutil module.
    """
    collector = CPUCollector(interval=TEST_INTERVAL)
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
    assert count["physical"] == PHYSICAL_CORES
    assert count["logical"] == LOGICAL_CORES

    # Check CPU frequency
    freq = metrics["frequency"]
    assert isinstance(freq["current"], float)
    assert isinstance(freq["min"], float)
    assert isinstance(freq["max"], float)
    assert freq["current"] == CURRENT_FREQ
    assert freq["min"] == MIN_FREQ
    assert freq["max"] == MAX_FREQ

    # Check CPU percentage
    percent = metrics["percent"]
    assert isinstance(percent["total"], float)
    assert MIN_PERCENT <= percent["total"] <= MAX_PERCENT
    assert isinstance(percent["per_cpu"], list)
    assert len(percent["per_cpu"]) == PHYSICAL_CORES
    assert all(MIN_PERCENT <= x <= MAX_PERCENT for x in percent["per_cpu"])
    assert percent["total"] == TOTAL_CPU_PERCENT
    assert percent["per_cpu"] == PER_CPU_PERCENT

    # Check CPU stats
    stats = metrics["stats"]
    assert isinstance(stats["ctx_switches"], int)
    assert isinstance(stats["interrupts"], int)
    assert isinstance(stats["soft_interrupts"], int)
    assert isinstance(stats["syscalls"], int)
    assert stats["ctx_switches"] == CTX_SWITCHES
    assert stats["interrupts"] == INTERRUPTS
    assert stats["soft_interrupts"] == SOFT_INTERRUPTS
    assert stats["syscalls"] == SYSCALLS


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_cpu_collector_no_frequency(mock_psutil: MockerFixture) -> None:
    """Test CPU metrics collection when frequency info is not available.

    Args:
        mock_psutil: Mocked psutil module.
    """
    # Mock cpu_freq to return None
    mock_psutil.cpu_freq.return_value = None

    collector = CPUCollector(interval=TEST_INTERVAL)
    metrics = await collector.collect()

    # Check that frequency values are None
    freq = metrics["frequency"]
    assert freq["current"] is None
    assert freq["min"] is None
    assert freq["max"] is None
