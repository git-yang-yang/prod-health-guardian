"""Tests for hardware metric collectors."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from prod_health_guardian.collectors.base import MetricCollector
from prod_health_guardian.collectors.cpu import CPUCollector
from prod_health_guardian.collectors.gpu import GPUCollector
from prod_health_guardian.collectors.memory import MemoryCollector

if TYPE_CHECKING:
    pass  # No type-only imports needed

# Constants
MIN_PERCENT = 0
MAX_PERCENT = 100
GPU_NAME = 'NVIDIA GeForce RTX 3080'
GPU_TEMP = 65
GPU_POWER = 220.0
GPU_MEMORY_TOTAL = 10737418240  # 10GB
GPU_MEMORY_USED = 5368709120    # 5GB
GPU_MEMORY_FREE = 5368709120    # 5GB
GPU_UTILIZATION = 75
GPU_MEMORY_UTILIZATION = 50
GPU_FAN_SPEED = 60


class TestCollector(MetricCollector):
    """Test implementation of MetricCollector."""

    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        return "test"

    async def collect(self) -> dict[str, int]:
        """Collect test metrics.

        Returns:
            dict[str, int]: Test metrics.
        """
        return {"value": 42}


def test_base_collector() -> None:
    """Test base collector functionality."""
    collector = TestCollector()
    assert collector.get_name() == "test"
    assert collector.is_available is True


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


@pytest.fixture
def mock_nvml() -> MagicMock:
    """Create a mock NVML module.
    
    Returns:
        MagicMock: Mocked NVML module
    """
    with patch('prod_health_guardian.collectors.gpu.pynvml') as mock:
        # Reset all mocks to ensure clean state
        mock.reset_mock()
        
        # Mock device handle
        handle = MagicMock()
        mock.nvmlDeviceGetHandleByIndex.return_value = handle
        
        # Mock device count
        mock.nvmlDeviceGetCount.return_value = 1
        
        # Mock device info
        mock.nvmlDeviceGetName.return_value = GPU_NAME.encode('utf-8')
        mock.nvmlDeviceGetTemperature.return_value = GPU_TEMP
        # Convert watts to milliwatts for power usage
        mock.nvmlDeviceGetPowerUsage.return_value = int(GPU_POWER * 1000)
        
        # Mock memory info
        memory = MagicMock()
        memory.total = GPU_MEMORY_TOTAL
        memory.used = GPU_MEMORY_USED
        memory.free = GPU_MEMORY_FREE
        mock.nvmlDeviceGetMemoryInfo.return_value = memory
        
        # Mock utilization info
        utilization = MagicMock()
        utilization.gpu = GPU_UTILIZATION
        utilization.memory = GPU_MEMORY_UTILIZATION
        mock.nvmlDeviceGetUtilizationRates.return_value = utilization
        
        # Mock fan speed
        mock.nvmlDeviceGetFanSpeed.return_value = GPU_FAN_SPEED
        
        yield mock
        
        # Clean up any initialized NVML instances
        try:
            mock.nvmlShutdown()
        except Exception:
            pass


@pytest.mark.collectors
def test_gpu_collector_init(mock_nvml: MagicMock) -> None:
    """Test GPU collector initialization.
    
    Args:
        mock_nvml: Mocked NVML module
    """
    collector = GPUCollector()
    assert collector.has_nvidia is True
    assert collector.device_count == 1
    mock_nvml.nvmlInit.assert_called_once()


@pytest.mark.collectors
def test_gpu_collector_metrics(mock_nvml: MagicMock) -> None:
    """Test GPU metrics collection.
    
    Args:
        mock_nvml: Mocked NVML module
    """
    collector = GPUCollector()
    metrics = collector.collect_metrics()
    
    assert metrics['device_count'] == 1
    assert len(metrics['devices']) == 1
    
    device = metrics['devices'][0]
    assert device['name'] == GPU_NAME
    assert device['temperature'] == GPU_TEMP
    assert device['power_usage'] == GPU_POWER
    assert device['memory_total'] == GPU_MEMORY_TOTAL
    assert device['memory_used'] == GPU_MEMORY_USED
    assert device['memory_free'] == GPU_MEMORY_FREE
    assert device['utilization'] == GPU_UTILIZATION
    assert device['memory_utilization'] == GPU_MEMORY_UTILIZATION
    assert device['fan_speed'] == GPU_FAN_SPEED


@pytest.mark.collectors
def test_gpu_collector_no_nvidia() -> None:
    """Test GPU collector behavior when NVIDIA GPUs are not available."""
    with patch('prod_health_guardian.collectors.gpu.HAS_NVIDIA', False):
        collector = GPUCollector()
        metrics = collector.collect_metrics()
        
        assert metrics['device_count'] == 0
        assert len(metrics['devices']) == 0


@pytest.mark.collectors
def test_gpu_collector_nvml_error() -> None:
    """Test GPU collector error handling."""
    with patch('prod_health_guardian.collectors.gpu.pynvml') as mock_nvml:
        # Create a mock error class
        mock_nvml.NVMLError = Exception
        
        # Mock that we have a GPU but fail to get any metrics
        mock_nvml.nvmlInit.return_value = None
        mock_nvml.nvmlDeviceGetCount.return_value = 1
        
        # Set all NVML functions to raise an error
        mock_nvml.nvmlDeviceGetHandleByIndex.side_effect = mock_nvml.NVMLError()
        mock_nvml.nvmlDeviceGetName.side_effect = mock_nvml.NVMLError()
        mock_nvml.nvmlDeviceGetTemperature.side_effect = mock_nvml.NVMLError()
        mock_nvml.nvmlDeviceGetPowerUsage.side_effect = mock_nvml.NVMLError()
        mock_nvml.nvmlDeviceGetMemoryInfo.side_effect = mock_nvml.NVMLError()
        mock_nvml.nvmlDeviceGetUtilizationRates.side_effect = mock_nvml.NVMLError()
        mock_nvml.nvmlDeviceGetFanSpeed.side_effect = mock_nvml.NVMLError()
        
        # Remove any return values that might override side effects
        mock_nvml.nvmlDeviceGetHandleByIndex.return_value = None
        mock_nvml.nvmlDeviceGetName.return_value = None
        mock_nvml.nvmlDeviceGetTemperature.return_value = None
        mock_nvml.nvmlDeviceGetPowerUsage.return_value = None
        mock_nvml.nvmlDeviceGetMemoryInfo.return_value = None
        mock_nvml.nvmlDeviceGetUtilizationRates.return_value = None
        mock_nvml.nvmlDeviceGetFanSpeed.return_value = None
        
        collector = GPUCollector()
        metrics = collector.collect_metrics()
        
        # Should report the correct device count but no devices due to error
        assert metrics['device_count'] == 1
        assert len(metrics['devices']) == 0


@pytest.mark.collectors
def test_gpu_collector_cleanup(mock_nvml: MagicMock) -> None:
    """Test GPU collector cleanup.
    
    Args:
        mock_nvml: Mocked NVML module
    """
    # Reset mock to ensure clean state
    mock_nvml.nvmlShutdown.reset_mock()
    
    collector = GPUCollector()
    del collector
    
    # Verify shutdown was called exactly once
    mock_nvml.nvmlShutdown.assert_called_once() 