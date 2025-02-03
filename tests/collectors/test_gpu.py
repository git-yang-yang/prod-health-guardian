"""Test GPU collector functionality."""

from typing import TYPE_CHECKING

import pynvml
import pytest

from prod_health_guardian.collectors.gpu import GPUCollector

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

# Test constants
GPU_NAME = "NVIDIA Test GPU"
GPU_TEMP = 65.0
GPU_POWER = 250.0  # Watts
GPU_MEM_TOTAL = 8589934592  # 8GB
GPU_MEM_USED = 4294967296  # 4GB
GPU_MEM_FREE = 4294967296  # 4GB
GPU_UTIL = 75.0
GPU_MEM_UTIL = 50.0
GPU_FAN = 80.0


@pytest.fixture
def mock_gpu_nvml(mocker: "MockerFixture") -> "MockerFixture":
    """Set up GPU NVML mocks.

    Args:
        mocker: Pytest mocker fixture.

    Returns:
        MockerFixture: Mocked NVML module.
    """
    mock = mocker.patch("prod_health_guardian.collectors.gpu.pynvml", autospec=True)
    mock.nvmlInit.return_value = None
    mock.nvmlDeviceGetCount.return_value = 1

    mock_handle = mocker.MagicMock()
    mock.nvmlDeviceGetHandleByIndex.return_value = mock_handle

    mock.nvmlDeviceGetName.return_value = GPU_NAME.encode()
    mock.nvmlDeviceGetTemperature.return_value = GPU_TEMP
    # Convert watts to milliwatts for NVML
    mock.nvmlDeviceGetPowerUsage.return_value = GPU_POWER * 1000

    mock_memory = mocker.MagicMock()
    mock_memory.total = GPU_MEM_TOTAL
    mock_memory.used = GPU_MEM_USED
    mock_memory.free = GPU_MEM_FREE
    mock.nvmlDeviceGetMemoryInfo.return_value = mock_memory

    mock_util = mocker.MagicMock()
    mock_util.gpu = GPU_UTIL
    mock_util.memory = GPU_MEM_UTIL
    mock.nvmlDeviceGetUtilizationRates.return_value = mock_util

    mock.nvmlDeviceGetFanSpeed.return_value = GPU_FAN

    return mock


@pytest.mark.asyncio
async def test_gpu_collector_metrics(mock_gpu_nvml: "MockerFixture") -> None:
    """Test GPU collector metrics collection.

    Args:
        mock_gpu_nvml: Mocked NVML fixture.
    """
    collector = GPUCollector()
    metrics = await collector.collect()

    # Validate metric structure
    assert isinstance(metrics, dict)
    assert all(isinstance(key, str) for key in metrics.keys())
    assert all(isinstance(value, (int, float, str)) for value in metrics.values())

    # Validate GPU metrics
    assert metrics["name"] == GPU_NAME
    assert metrics["temperature"] == GPU_TEMP
    assert metrics["power_watts"] == GPU_POWER
    assert metrics["memory_total"] == GPU_MEM_TOTAL
    assert metrics["memory_used"] == GPU_MEM_USED
    assert metrics["memory_free"] == GPU_MEM_FREE
    assert metrics["gpu_utilization"] == GPU_UTIL
    assert metrics["memory_utilization"] == GPU_MEM_UTIL
    assert metrics["fan_speed"] == GPU_FAN


@pytest.mark.asyncio
async def test_gpu_collector_no_gpu(mock_gpu_nvml: "MockerFixture") -> None:
    """Test GPU collector when no GPU is available.

    Args:
        mock_gpu_nvml: Mocked NVML fixture.
    """
    # Mock NVML initialization to fail
    mock_gpu_nvml.nvmlInit.side_effect = pynvml.NVMLError_LibraryNotFound()

    collector = GPUCollector()
    metrics = await collector.collect()

    # All metrics should be zero/default
    assert metrics["name"] == "No GPU"
    assert metrics["temperature"] == 0.0
    assert metrics["power_watts"] == 0.0
    assert metrics["memory_total"] == 0
    assert metrics["memory_used"] == 0
    assert metrics["memory_free"] == 0
    assert metrics["gpu_utilization"] == 0.0
    assert metrics["memory_utilization"] == 0.0
    assert metrics["fan_speed"] == 0.0


@pytest.mark.asyncio
async def test_gpu_collector_no_power(mock_gpu_nvml: "MockerFixture") -> None:
    """Test GPU collector when power information is not available.

    Args:
        mock_gpu_nvml: Mocked NVML fixture.
    """
    # Mock power usage to raise an exception
    mock_gpu_nvml.nvmlDeviceGetPowerUsage.side_effect = pynvml.NVMLError_NotSupported()

    collector = GPUCollector()
    metrics = await collector.collect()

    # Power should be 0, other metrics should be normal
    assert metrics["name"] == GPU_NAME
    assert metrics["power_watts"] == 0.0
    assert metrics["memory_total"] == GPU_MEM_TOTAL
    assert metrics["memory_used"] == GPU_MEM_USED
    assert metrics["memory_free"] == GPU_MEM_FREE
    assert metrics["gpu_utilization"] == GPU_UTIL
    assert metrics["memory_utilization"] == GPU_MEM_UTIL
    assert metrics["fan_speed"] == GPU_FAN
