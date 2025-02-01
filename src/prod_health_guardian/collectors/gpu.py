"""GPU metrics collector module."""

import logging
from typing import Any

import pynvml

logger = logging.getLogger(__name__)


class GPUCollector:
    """NVIDIA GPU metrics collector.

    This collector gathers various GPU metrics including:
    - Device count and names
    - Temperature and power usage
    - Memory usage (total, used, free)
    - Utilization (GPU and memory)
    - Fan speed

    The collector uses NVIDIA's NVML library through pynvml to access
    GPU metrics. If no NVIDIA GPU is available or if there are any
    errors accessing the GPU, the collector will return empty metrics.
    """

    def __init__(self) -> None:
        """Initialize GPU collector.

        Attempts to initialize NVML library. If initialization fails,
        the collector will be marked as not having NVIDIA GPU access.
        """
        self.has_nvidia = False
        self.device_count = 0

        try:
            pynvml.nvmlInit()
            self.has_nvidia = True
            self.device_count = pynvml.nvmlDeviceGetCount()
            logger.info("NVML initialized with %d GPU(s)", self.device_count)
        except pynvml.NVMLError as e:
            logger.warning("Failed to initialize NVML: %s", e)

    def collect_metrics(self) -> dict[str, Any]:
        """Collect GPU metrics.

        Returns:
            dict[str, Any]: GPU metrics including device count and per-device metrics.
                If no GPU is available, returns minimal metrics with device_count=0.
        """
        metrics = {
            "device_count": self.device_count,
            "devices": [],
        }

        if not self.has_nvidia:
            return metrics

        try:
            for i in range(self.device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                device_metrics = self._collect_device_metrics(handle)
                if device_metrics:
                    metrics["devices"].append(device_metrics)
        except pynvml.NVMLError as e:
            logger.error("Error collecting GPU metrics: %s", e)

        return metrics

    def _collect_device_metrics(self, handle: Any) -> dict[str, Any]:
        """Collect metrics for a single GPU device.

        Args:
            handle: NVML device handle.

        Returns:
            dict[str, Any]: Device metrics including temperature, memory usage, etc.
                Returns None if there's an error collecting metrics.
        """
        try:
            # Get basic device info
            name = pynvml.nvmlDeviceGetName(handle).decode()
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts

            # Get memory info
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

            # Get utilization rates
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

            # Get fan speed
            try:
                fan = pynvml.nvmlDeviceGetFanSpeed(handle)
            except pynvml.NVMLError:
                fan = 0

            return {
                "name": name,
                "temperature": float(temp),
                "power_usage": float(power),
                "memory_total": memory.total,
                "memory_used": memory.used,
                "memory_free": memory.free,
                "utilization": float(utilization.gpu),
                "memory_utilization": float(utilization.memory),
                "fan_speed": float(fan),
            }
        except pynvml.NVMLError as e:
            logger.error("Error collecting device metrics: %s", e)
            return None
