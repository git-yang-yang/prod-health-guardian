"""Shared fixtures for collector tests."""

from typing import TYPE_CHECKING, Union

import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

# Type aliases
CPUMetric = Union[float, list[float]]

# CPU test constants
CPU_PHYSICAL_CORES = 4
CPU_LOGICAL_CORES = 8
CPU_FREQ_CURRENT = 3700.0
CPU_FREQ_MIN = 2200.0
CPU_FREQ_MAX = 4500.0
CPU_TOTAL_PERCENT = 25.5
CPU_PER_CPU_PERCENT = [20.0, 30.0, 25.0, 27.0]
CPU_CTX_SWITCHES = 1000
CPU_INTERRUPTS = 500
CPU_SOFT_INTERRUPTS = 200
CPU_SYSCALLS = 300

# Memory test constants
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

# GPU test constants
GPU_NAME = "NVIDIA GeForce RTX 3080"
GPU_TEMP = 65.0
GPU_POWER_WATTS = 220.5
GPU_MEMORY_TOTAL = 10_737_418_240  # 10GB
GPU_MEMORY_USED = 4_294_967_296  # 4GB
GPU_MEMORY_FREE = 6_442_450_944  # 6GB
GPU_UTILIZATION = 85.5
GPU_MEMORY_UTILIZATION = 40.0
GPU_FAN_SPEED = 75.0


@pytest.fixture
def mock_cpu_psutil(mocker: "MockerFixture") -> "MockerFixture":
    """Mock psutil for CPU tests.

    Args:
        mocker: Pytest mocker fixture.

    Returns:
        MockerFixture: Configured mocker.
    """
    mock = mocker.patch("prod_health_guardian.collectors.cpu.psutil")

    # Set up mock values
    mock.cpu_count.side_effect = (
        lambda logical: CPU_LOGICAL_CORES if logical else CPU_PHYSICAL_CORES
    )
    mock.cpu_freq.return_value.current = CPU_FREQ_CURRENT
    mock.cpu_freq.return_value.min = CPU_FREQ_MIN
    mock.cpu_freq.return_value.max = CPU_FREQ_MAX
    mock.cpu_percent.return_value = CPU_TOTAL_PERCENT

    def cpu_percent_side_effect(interval: float, percpu: bool = False) -> CPUMetric:
        """Side effect for cpu_percent to handle both total and per-CPU metrics."""
        return CPU_PER_CPU_PERCENT if percpu else CPU_TOTAL_PERCENT

    mock.cpu_percent.side_effect = cpu_percent_side_effect
    mock.cpu_stats.return_value.ctx_switches = CPU_CTX_SWITCHES
    mock.cpu_stats.return_value.interrupts = CPU_INTERRUPTS
    mock.cpu_stats.return_value.soft_interrupts = CPU_SOFT_INTERRUPTS
    mock.cpu_stats.return_value.syscalls = CPU_SYSCALLS

    return mock


@pytest.fixture
def mock_memory_psutil(mocker: "MockerFixture") -> "MockerFixture":
    """Mock psutil for memory tests.

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


@pytest.fixture
def mock_gpu_nvml(mocker: "MockerFixture") -> "MockerFixture":
    """Mock NVML for GPU tests.

    Args:
        mocker: Pytest mocker fixture.

    Returns:
        MockerFixture: Configured mocker.
    """
    mock = mocker.patch("prod_health_guardian.collectors.gpu.pynvml")

    # Set up mock values
    mock.nvmlDeviceGetName.return_value = GPU_NAME.encode()
    mock.nvmlDeviceGetTemperature.return_value = GPU_TEMP
    # Convert watts to milliwatts
    mock.nvmlDeviceGetPowerUsage.return_value = int(GPU_POWER_WATTS * 1000)

    # Memory info
    class MemoryInfo:
        total = GPU_MEMORY_TOTAL
        used = GPU_MEMORY_USED
        free = GPU_MEMORY_FREE

    mock.nvmlDeviceGetMemoryInfo.return_value = MemoryInfo()

    # Utilization rates
    class UtilizationRates:
        gpu = GPU_UTILIZATION
        memory = GPU_MEMORY_UTILIZATION

    mock.nvmlDeviceGetUtilizationRates.return_value = UtilizationRates()
    mock.nvmlDeviceGetFanSpeed.return_value = GPU_FAN_SPEED

    return mock
