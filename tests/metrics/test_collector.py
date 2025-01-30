"""Tests for the metrics collector module."""

import re
from typing import TYPE_CHECKING

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
    pass  # No unused imports

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


class AsyncMock:
    """Helper class to create async mock objects."""

    def __init__(self, return_value):
        """Initialize with return value."""
        self.return_value = return_value

    async def __call__(self, *args, **kwargs):
        """Async call that returns the stored value."""
        return self.return_value


@pytest.fixture
def mock_collectors(mocker: MockerFixture) -> None:
    """Mock hardware collectors.
    
    Args:
        mocker: Pytest mocker fixture.
    """
    # Mock CPU collector
    mock_cpu = mocker.patch("prod_health_guardian.metrics.collectors.CPUCollector")
    mock_cpu.return_value.collect = AsyncMock({
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
    })

    # Mock Memory collector
    mock_memory = mocker.patch(
        "prod_health_guardian.metrics.collectors.MemoryCollector"
    )
    mock_memory.return_value.collect = AsyncMock({
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
    })

    # Mock GPU collector
    mock_gpu = mocker.patch("prod_health_guardian.metrics.collectors.GPUCollector")
    mock_gpu.return_value.collect_metrics.return_value = {
        "device_count": GPU_DEVICE_COUNT,
        "devices": [{
            "name": GPU_NAME,
            "temperature": GPU_TEMP_1,
            "power_usage": GPU_POWER_1,
            "memory_total": GPU_MEMORY_TOTAL,
            "memory_used": GPU_MEMORY_USED_1,
            "memory_free": GPU_MEMORY_FREE_1,
            "utilization": GPU_UTIL_1,
            "memory_utilization": GPU_MEM_UTIL_1,
            "fan_speed": GPU_FAN_1
        }, {
            "name": GPU_NAME,
            "temperature": GPU_TEMP_2,
            "power_usage": GPU_POWER_2,
            "memory_total": GPU_MEMORY_TOTAL,
            "memory_used": GPU_MEMORY_USED_2,
            "memory_free": GPU_MEMORY_FREE_2,
            "utilization": GPU_UTIL_2,
            "memory_utilization": GPU_MEM_UTIL_2,
            "fan_speed": GPU_FAN_2
        }]
    }


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
    assert metrics.cpu.count["physical"] == CPU_PHYSICAL_COUNT
    assert metrics.cpu.count["logical"] == CPU_LOGICAL_COUNT
    assert metrics.cpu.frequency["current"] == CPU_FREQ_CURRENT
    assert len(metrics.cpu.percent["per_cpu"]) == CPU_PHYSICAL_COUNT

    # Verify Memory metrics
    assert metrics.memory.virtual["total"] == MEM_VIRTUAL_TOTAL
    assert metrics.memory.swap["total"] == MEM_SWAP_TOTAL

    # Verify GPU metrics
    assert metrics.gpu.device_count == GPU_DEVICE_COUNT
    assert len(metrics.gpu.devices) == GPU_DEVICE_COUNT
    assert metrics.gpu.devices[0].name == GPU_NAME
    assert metrics.gpu.devices[0].temperature == GPU_TEMP_1
    assert metrics.gpu.devices[1].utilization == GPU_UTIL_2

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
    assert f"cpu_physical_count {CPU_PHYSICAL_COUNT}" in metrics_text
    assert f"cpu_logical_count {CPU_LOGICAL_COUNT}" in metrics_text
    assert f"cpu_frequency_current_mhz {CPU_FREQ_CURRENT}" in metrics_text
    assert f'cpu_percent_per_cpu{{core="0"}} {CPU_PERCENT_PER_CPU[0]}' in metrics_text
    assert f"cpu_ctx_switches_total {CPU_CTX_SWITCHES}" in metrics_text

    # Memory metrics - verify values by extracting numbers
    pattern = r"memory_virtual_total_bytes\s+([\d.e+-]+)"
    memory_virtual_match = re.search(pattern, metrics_text)
    pattern = r"memory_swap_total_bytes\s+([\d.e+-]+)"
    memory_swap_match = re.search(pattern, metrics_text)
    
    assert memory_virtual_match is not None, (
        "memory_virtual_total_bytes metric not found"
    )
    assert memory_swap_match is not None, (
        "memory_swap_total_bytes metric not found"
    )
    assert float(memory_virtual_match.group(1)) == float(MEM_VIRTUAL_TOTAL)
    assert float(memory_swap_match.group(1)) == float(MEM_SWAP_TOTAL)

    # GPU metrics
    assert f"gpu_device_count {GPU_DEVICE_COUNT}" in metrics_text
    
    # GPU 0 metrics
    gpu0_base = f'{{gpu_id="0",name="{GPU_NAME}"}}'
    assert f'gpu_temperature_celsius{gpu0_base} {GPU_TEMP_1}' in metrics_text
    assert f'gpu_power_watts{gpu0_base} {GPU_POWER_1}' in metrics_text
    
    # Use regex to extract and compare GPU memory value
    pattern = rf'gpu_memory_total_bytes{gpu0_base}\s+([\d.e+-]+)'
    gpu_memory_match = re.search(pattern, metrics_text)
    assert gpu_memory_match is not None, (
        "gpu_memory_total_bytes metric not found"
    )
    assert float(gpu_memory_match.group(1)) == float(GPU_MEMORY_TOTAL)
    
    assert f'gpu_utilization_percent{gpu0_base} {GPU_UTIL_1}' in metrics_text
    assert f'gpu_fan_speed_percent{gpu0_base} {GPU_FAN_1}' in metrics_text
    
    # GPU 1 metrics
    gpu1_base = f'{{gpu_id="1",name="{GPU_NAME}"}}'
    assert f'gpu_temperature_celsius{gpu1_base} {GPU_TEMP_2}' in metrics_text
    assert f'gpu_utilization_percent{gpu1_base} {GPU_UTIL_2}' in metrics_text 