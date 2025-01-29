"""Tests for the metrics collector module."""

from typing import TYPE_CHECKING, Any

import pytest
from prometheus_client import REGISTRY

from prod_health_guardian.metrics.collectors import MetricsCollector

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

@pytest.fixture(autouse=True)
def clear_registry() -> None:
    """Clear the Prometheus registry before each test."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)

# CPU test constants
CPU_PHYSICAL_COUNT = 4
CPU_LOGICAL_COUNT = 8
CPU_FREQ_CURRENT = 2400.0
CPU_FREQ_MIN = 2200.0
CPU_FREQ_MAX = 3200.0
CPU_PERCENT_TOTAL = 25.5
CPU_PERCENT_PER_CPU = [20.0, 30.0, 25.0, 27.0]
CPU_CTX_SWITCHES = 1000
CPU_INTERRUPTS = 500
CPU_SOFT_INTERRUPTS = 200
CPU_SYSCALLS = 300

# Memory test constants
MEM_VIRTUAL_TOTAL = 16_000_000_000
MEM_VIRTUAL_AVAILABLE = 8_000_000_000
MEM_VIRTUAL_USED = 8_000_000_000
MEM_VIRTUAL_FREE = 8_000_000_000
MEM_VIRTUAL_PERCENT = 50.0
MEM_SWAP_TOTAL = 8_000_000_000
MEM_SWAP_USED = 1_000_000_000
MEM_SWAP_FREE = 7_000_000_000
MEM_SWAP_PERCENT = 12.5
MEM_SWAP_SIN = 100
MEM_SWAP_SOUT = 50

@pytest.fixture
def mock_cpu_data() -> dict[str, Any]:
    """Mock CPU metrics data."""
    return {
        "count": {
            "physical": CPU_PHYSICAL_COUNT,
            "logical": CPU_LOGICAL_COUNT
        },
        "frequency": {
            "current": CPU_FREQ_CURRENT,
            "min": CPU_FREQ_MIN,
            "max": CPU_FREQ_MAX
        },
        "percent": {
            "total": CPU_PERCENT_TOTAL,
            "per_cpu": CPU_PERCENT_PER_CPU
        },
        "stats": {
            "ctx_switches": CPU_CTX_SWITCHES,
            "interrupts": CPU_INTERRUPTS,
            "soft_interrupts": CPU_SOFT_INTERRUPTS,
            "syscalls": CPU_SYSCALLS
        }
    }

@pytest.fixture
def mock_memory_data() -> dict[str, Any]:
    """Mock memory metrics data."""
    return {
        "virtual": {
            "total": MEM_VIRTUAL_TOTAL,
            "available": MEM_VIRTUAL_AVAILABLE,
            "used": MEM_VIRTUAL_USED,
            "free": MEM_VIRTUAL_FREE,
            "percent": MEM_VIRTUAL_PERCENT
        },
        "swap": {
            "total": MEM_SWAP_TOTAL,
            "used": MEM_SWAP_USED,
            "free": MEM_SWAP_FREE,
            "percent": MEM_SWAP_PERCENT,
            "sin": MEM_SWAP_SIN,
            "sout": MEM_SWAP_SOUT
        }
    }

@pytest.fixture
def collector(mocker: "MockerFixture") -> MetricsCollector:
    """Create a MetricsCollector with mocked collectors."""
    collector = MetricsCollector()
    mocker.patch.object(collector.cpu_collector, "collect")
    mocker.patch.object(collector.memory_collector, "collect")
    return collector

@pytest.mark.asyncio
async def test_collect_metrics(
    collector: MetricsCollector,
    mock_cpu_data: dict[str, Any],
    mock_memory_data: dict[str, Any]
) -> None:
    """Test collecting metrics from all collectors."""
    # Setup mocks
    collector.cpu_collector.collect.return_value = mock_cpu_data
    collector.memory_collector.collect.return_value = mock_memory_data

    # Collect metrics
    metrics = await collector.collect_metrics()

    # Verify CPU metrics
    assert metrics.cpu.count["physical"] == CPU_PHYSICAL_COUNT
    assert metrics.cpu.count["logical"] == CPU_LOGICAL_COUNT
    assert metrics.cpu.frequency["current"] == CPU_FREQ_CURRENT
    assert metrics.cpu.frequency["min"] == CPU_FREQ_MIN
    assert metrics.cpu.frequency["max"] == CPU_FREQ_MAX
    assert metrics.cpu.percent["total"] == CPU_PERCENT_TOTAL
    assert metrics.cpu.percent["per_cpu"] == CPU_PERCENT_PER_CPU
    assert metrics.cpu.stats["ctx_switches"] == CPU_CTX_SWITCHES
    assert metrics.cpu.stats["interrupts"] == CPU_INTERRUPTS
    assert metrics.cpu.stats["soft_interrupts"] == CPU_SOFT_INTERRUPTS
    assert metrics.cpu.stats["syscalls"] == CPU_SYSCALLS

    # Verify memory metrics
    assert metrics.memory.virtual["total"] == MEM_VIRTUAL_TOTAL
    assert metrics.memory.virtual["available"] == MEM_VIRTUAL_AVAILABLE
    assert metrics.memory.virtual["used"] == MEM_VIRTUAL_USED
    assert metrics.memory.virtual["free"] == MEM_VIRTUAL_FREE
    assert metrics.memory.virtual["percent"] == MEM_VIRTUAL_PERCENT
    assert metrics.memory.swap["total"] == MEM_SWAP_TOTAL
    assert metrics.memory.swap["used"] == MEM_SWAP_USED
    assert metrics.memory.swap["free"] == MEM_SWAP_FREE
    assert metrics.memory.swap["percent"] == MEM_SWAP_PERCENT
    assert metrics.memory.swap["sin"] == MEM_SWAP_SIN
    assert metrics.memory.swap["sout"] == MEM_SWAP_SOUT

@pytest.mark.asyncio
async def test_update_prometheus_metrics(
    collector: MetricsCollector,
    mock_cpu_data: dict[str, Any],
    mock_memory_data: dict[str, Any]
) -> None:
    """Test updating Prometheus metrics from collected data."""
    # First collect metrics
    collector.cpu_collector.collect.return_value = mock_cpu_data
    collector.memory_collector.collect.return_value = mock_memory_data
    metrics = await collector.collect_metrics()
    
    # Then update Prometheus metrics
    collector.update_prometheus_metrics(metrics)

    # Verify CPU metrics
    assert REGISTRY.get_sample_value("cpu_physical_count") == CPU_PHYSICAL_COUNT
    assert REGISTRY.get_sample_value("cpu_logical_count") == CPU_LOGICAL_COUNT
    assert REGISTRY.get_sample_value("cpu_frequency_current_mhz") == CPU_FREQ_CURRENT
    assert REGISTRY.get_sample_value("cpu_frequency_min_mhz") == CPU_FREQ_MIN
    assert REGISTRY.get_sample_value("cpu_frequency_max_mhz") == CPU_FREQ_MAX
    assert REGISTRY.get_sample_value("cpu_percent_total") == CPU_PERCENT_TOTAL
    for i, percent in enumerate(CPU_PERCENT_PER_CPU):
        assert REGISTRY.get_sample_value(
            "cpu_percent_per_cpu",
            {"core": str(i)}
        ) == percent
    assert REGISTRY.get_sample_value("cpu_ctx_switches_total") == CPU_CTX_SWITCHES
    assert REGISTRY.get_sample_value("cpu_interrupts_total") == CPU_INTERRUPTS
    assert REGISTRY.get_sample_value("cpu_soft_interrupts_total") == CPU_SOFT_INTERRUPTS
    assert REGISTRY.get_sample_value("cpu_syscalls_total") == CPU_SYSCALLS

    # Verify memory metrics
    assert REGISTRY.get_sample_value(
        "memory_virtual_total_bytes"
    ) == MEM_VIRTUAL_TOTAL
    assert REGISTRY.get_sample_value(
        "memory_virtual_available_bytes"
    ) == MEM_VIRTUAL_AVAILABLE
    assert REGISTRY.get_sample_value(
        "memory_virtual_used_bytes"
    ) == MEM_VIRTUAL_USED
    assert REGISTRY.get_sample_value(
        "memory_virtual_free_bytes"
    ) == MEM_VIRTUAL_FREE
    assert REGISTRY.get_sample_value("memory_virtual_percent") == MEM_VIRTUAL_PERCENT
    assert REGISTRY.get_sample_value("memory_swap_total_bytes") == MEM_SWAP_TOTAL
    assert REGISTRY.get_sample_value("memory_swap_used_bytes") == MEM_SWAP_USED
    assert REGISTRY.get_sample_value("memory_swap_free_bytes") == MEM_SWAP_FREE
    assert REGISTRY.get_sample_value("memory_swap_percent") == MEM_SWAP_PERCENT
    assert REGISTRY.get_sample_value("memory_swap_sin_total") == MEM_SWAP_SIN
    assert REGISTRY.get_sample_value("memory_swap_sout_total") == MEM_SWAP_SOUT 