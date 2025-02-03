"""Tests for the metrics collector module."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from prometheus_client import REGISTRY
from pytest_mock import MockerFixture

from prod_health_guardian.metrics.collectors import MetricsCollector
from prod_health_guardian.models.metrics import (
    CPUMetrics,
    GPUMetrics,
    MemoryMetrics,
    SystemMetrics,
)

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


@pytest.fixture(autouse=True)
def clear_registry() -> None:
    """Clear the Prometheus registry before each test."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)


# Test constants
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

# GPU test constants
GPU_DEVICE_COUNT = 2
GPU_NAME = "NVIDIA GeForce RTX 3080"
GPU_TEMP_1 = 65.0
GPU_TEMP_2 = 67.0
GPU_POWER_1 = 220.5
GPU_POWER_2 = 225.5
GPU_MEMORY_TOTAL = 10_737_418_240
GPU_MEMORY_USED_1 = 4_294_967_296
GPU_MEMORY_USED_2 = 5_368_709_120
GPU_MEMORY_FREE_1 = 6_442_450_944
GPU_MEMORY_FREE_2 = 5_368_709_120
GPU_UTIL_1 = 85.5
GPU_UTIL_2 = 90.5
GPU_MEM_UTIL_1 = 40.0
GPU_MEM_UTIL_2 = 50.0
GPU_FAN_1 = 75.0
GPU_FAN_2 = 80.0


@pytest.fixture
def mock_collectors(mocker: MockerFixture) -> None:
    """Mock hardware collectors.

    Args:
        mocker: Pytest mocker fixture.
    """
    # Mock CPU collector
    mock_cpu = mocker.patch("prod_health_guardian.metrics.collectors.CPUCollector")
    mock_cpu.return_value.collect = AsyncMock(
        return_value={
            "physical_cores": CPU_PHYSICAL_COUNT,
            "logical_cores": CPU_LOGICAL_COUNT,
            "cpu_freq_current": CPU_FREQ_CURRENT,
            "cpu_freq_min": CPU_FREQ_MIN,
            "cpu_freq_max": CPU_FREQ_MAX,
            "cpu_percent": CPU_PERCENT_TOTAL,
            "per_cpu_percent": CPU_PERCENT_PER_CPU,
            "ctx_switches": CPU_CTX_SWITCHES,
            "interrupts": CPU_INTERRUPTS,
            "soft_interrupts": CPU_SOFT_INTERRUPTS,
            "syscalls": CPU_SYSCALLS,
        }
    )

    # Mock Memory collector
    mock_memory = mocker.patch(
        "prod_health_guardian.metrics.collectors.MemoryCollector"
    )
    mock_memory.return_value.collect = AsyncMock(
        return_value={
            "total": MEM_VIRTUAL_TOTAL,
            "available": MEM_VIRTUAL_AVAILABLE,
            "used": MEM_VIRTUAL_USED,
            "free": MEM_VIRTUAL_FREE,
            "percent": MEM_VIRTUAL_PERCENT,
            "swap_total": MEM_SWAP_TOTAL,
            "swap_used": MEM_SWAP_USED,
            "swap_free": MEM_SWAP_FREE,
            "swap_percent": MEM_SWAP_PERCENT,
            "swap_in": MEM_SWAP_SIN,
            "swap_out": MEM_SWAP_SOUT,
        }
    )

    # Mock GPU collector
    mock_gpu = mocker.patch("prod_health_guardian.metrics.collectors.GPUCollector")
    mock_gpu.return_value.collect = AsyncMock(
        return_value={
            "name": GPU_NAME,
            "temperature": GPU_TEMP_1,
            "power_watts": GPU_POWER_1,
            "memory_total": GPU_MEMORY_TOTAL,
            "memory_used": GPU_MEMORY_USED_1,
            "memory_free": GPU_MEMORY_FREE_1,
            "gpu_utilization": GPU_UTIL_1,
            "memory_utilization": GPU_MEM_UTIL_1,
            "fan_speed": GPU_FAN_1,
        }
    )


@pytest.fixture
def collector(mocker: MockerFixture) -> MetricsCollector:
    """Create a MetricsCollector with mocked collectors."""
    collector = MetricsCollector()
    mocker.patch.object(collector.cpu_collector, "collect")
    mocker.patch.object(collector.memory_collector, "collect")
    return collector


@pytest.mark.asyncio
async def test_collect_metrics(mock_collectors: None) -> None:
    """Test metrics collection.

    Args:
        mock_collectors: Mocked hardware collectors.
    """
    collector = MetricsCollector()
    metrics = await collector.collect_metrics()

    assert isinstance(metrics, SystemMetrics)
    assert isinstance(metrics.cpu, CPUMetrics)
    assert isinstance(metrics.memory, MemoryMetrics)
    assert isinstance(metrics.gpu, GPUMetrics)

    # Verify CPU metrics
    assert metrics.cpu.physical_cores == CPU_PHYSICAL_COUNT
    assert metrics.cpu.logical_cores == CPU_LOGICAL_COUNT
    assert metrics.cpu.cpu_freq_current == CPU_FREQ_CURRENT
    assert len(metrics.cpu.per_cpu_percent) == CPU_PHYSICAL_COUNT

    # Verify Memory metrics
    assert metrics.memory.total == MEM_VIRTUAL_TOTAL
    assert metrics.memory.swap_total == MEM_SWAP_TOTAL

    # Verify GPU metrics
    assert metrics.gpu.name == GPU_NAME
    assert metrics.gpu.temperature == GPU_TEMP_1
    assert metrics.gpu.power_watts == GPU_POWER_1


@pytest.mark.asyncio
async def test_update_prometheus_metrics(mock_collectors: None) -> None:
    """Test Prometheus metrics update.

    Args:
        mock_collectors: Mocked hardware collectors.
    """
    collector = MetricsCollector()
    metrics = await collector.collect_metrics()
    collector.update_prometheus_metrics(metrics)

    metrics_text = collector.get_prometheus_metrics().decode()

    # CPU metrics
    assert f"cpu_physical_count {CPU_PHYSICAL_COUNT}.0" in metrics_text
    assert f"cpu_logical_count {CPU_LOGICAL_COUNT}.0" in metrics_text
    assert f"cpu_frequency_current_mhz {CPU_FREQ_CURRENT}" in metrics_text
    assert f'cpu_percent_per_cpu{{core="0"}} {CPU_PERCENT_PER_CPU[0]}' in metrics_text
    assert f"cpu_ctx_switches_total {CPU_CTX_SWITCHES}.0" in metrics_text

    # Memory metrics - using scientific notation format
    assert "memory_virtual_total_bytes 1.6e+010" in metrics_text
    assert "memory_swap_total_bytes 8e+09" in metrics_text

    # GPU metrics
    assert (
        f'gpu_temperature_celsius{{gpu_id="0",name="{GPU_NAME}"}} {GPU_TEMP_1}'
        in metrics_text
    )
    assert (
        f'gpu_power_watts{{gpu_id="0",name="{GPU_NAME}"}} {GPU_POWER_1}' in metrics_text
    )
