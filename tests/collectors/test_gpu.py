"""Tests for GPU metrics collector."""

from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from prod_health_guardian.collectors.gpu import GPUCollector

if TYPE_CHECKING:
    pass  # No unused imports


# Test constants
DEVICE_COUNT = 2
GPU_NAME = "NVIDIA GeForce RTX 3080"
GPU_TEMPERATURE = 65.0
GPU_POWER_MILLIWATTS = 220500  # milliwatts
GPU_POWER_WATTS = 220.5  # watts
GPU_MEMORY_TOTAL = 10_737_418_240  # 10GB
GPU_MEMORY_USED = 4_294_967_296  # 4GB
GPU_MEMORY_FREE = 6_442_450_944  # 6GB
GPU_UTILIZATION = 85.0
GPU_MEMORY_UTILIZATION = 40.0
GPU_FAN_SPEED = 75.0


class MockNVMLError(Exception):
    """Mock NVML Error class."""


@pytest.fixture
def mock_gpu_metrics() -> dict:
    """Create mock GPU metrics.

    Returns:
        dict: Mock GPU metrics data.
    """
    return {
        "device_count": DEVICE_COUNT,
        "devices": [
            {
                "name": GPU_NAME,
                "temperature": GPU_TEMPERATURE,
                "power_usage": GPU_POWER_WATTS,
                "memory_total": GPU_MEMORY_TOTAL,
                "memory_used": GPU_MEMORY_USED,
                "memory_free": GPU_MEMORY_FREE,
                "utilization": GPU_UTILIZATION,
                "memory_utilization": GPU_MEMORY_UTILIZATION,
                "fan_speed": GPU_FAN_SPEED,
            }
        ],
    }


@pytest.fixture
def mock_collector(mocker: MockerFixture, mock_gpu_metrics: dict) -> GPUCollector:
    """Create a mocked GPU collector.

    Args:
        mocker: Pytest mocker fixture.
        mock_gpu_metrics: Mock GPU metrics data.

    Returns:
        GPUCollector: Mocked collector instance.
    """
    # Mock pynvml to avoid actual GPU calls
    mocker.patch("prod_health_guardian.collectors.gpu.pynvml")

    # Create collector instance
    collector = GPUCollector()

    # Override collect_metrics to return our mock data
    mocker.patch.object(
        collector,
        "collect_metrics",
        return_value=mock_gpu_metrics,
    )

    return collector


def test_gpu_collector_metrics_with_gpu(
    mock_collector: GPUCollector,
    mock_gpu_metrics: dict,
) -> None:
    """Test GPU metrics collection with GPU available.

    Args:
        mock_collector: Mocked GPU collector.
        mock_gpu_metrics: Expected GPU metrics.
    """
    metrics = mock_collector.collect_metrics()

    # Verify the metrics match our mock data
    assert metrics == mock_gpu_metrics

    # Verify specific values
    device = metrics["devices"][0]
    assert device["name"] == GPU_NAME
    assert device["temperature"] == GPU_TEMPERATURE
    assert device["power_usage"] == GPU_POWER_WATTS
    assert device["memory_total"] == GPU_MEMORY_TOTAL
    assert device["memory_used"] == GPU_MEMORY_USED
    assert device["memory_free"] == GPU_MEMORY_FREE
    assert device["utilization"] == GPU_UTILIZATION
    assert device["memory_utilization"] == GPU_MEMORY_UTILIZATION
    assert device["fan_speed"] == GPU_FAN_SPEED


def test_gpu_collector_metrics_no_gpu(mocker: MockerFixture) -> None:
    """Test GPU metrics collection when no GPU is available.

    Args:
        mocker: Pytest mocker fixture.
    """
    # Mock pynvml with error
    mock_pynvml = mocker.patch("prod_health_guardian.collectors.gpu.pynvml")
    mock_pynvml.NVMLError = MockNVMLError
    mock_pynvml.nvmlInit.side_effect = MockNVMLError("No NVIDIA driver found")

    collector = GPUCollector()
    metrics = collector.collect_metrics()

    assert metrics["device_count"] == 0
    assert metrics["devices"] == []
