"""GPU metrics collector module."""

import logging
from typing import Union

import pynvml

from .base import BaseCollector

logger = logging.getLogger(__name__)


class GPUCollector(BaseCollector):
    """NVIDIA GPU metrics collector.

    This collector gathers various GPU metrics including:
    - Device name and status
    - Temperature and power usage
    - Memory usage (total, used, free)
    - Utilization (GPU and memory)
    - Fan speed

    The collector uses NVIDIA's NVML library through pynvml to access
    GPU metrics. If no NVIDIA GPU is available or if there are any
    errors accessing the GPU, the collector will return default metrics.
    """

    def __init__(self, interval: float = 1.0) -> None:
        """Initialize GPU collector.

        Args:
            interval: Time interval in seconds for metric collection.
        """
        self.interval = interval
        self.has_nvidia = False
        self.device_count = 0
        self.handle = None

        try:
            pynvml.nvmlInit()
            self.has_nvidia = True
            self.device_count = pynvml.nvmlDeviceGetCount()
            if self.device_count > 0:
                self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            logger.info("NVML initialized with %d GPU(s)", self.device_count)
        except Exception as e:
            logger.warning("Failed to initialize NVML: %s", str(e))

    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        return "gpu"

    async def collect(self) -> dict[str, Union[int, float, str]]:
        """Collect GPU metrics.

        Returns:
            dict[str, Union[int, float, str]]: GPU metrics including temperature,
                memory usage, utilization, etc. If no GPU is available or on error,
                returns default metrics with zeros.
        """
        if not self.has_nvidia or not self.handle:
            return {
                "name": "No GPU",
                "temperature": 0.0,
                "power_watts": 0.0,
                "memory_total": 0,
                "memory_used": 0,
                "memory_free": 0,
                "gpu_utilization": 0.0,
                "memory_utilization": 0.0,
                "fan_speed": 0.0,
            }

        try:
            # Get basic device info
            name = pynvml.nvmlDeviceGetName(self.handle).decode()
            temp = pynvml.nvmlDeviceGetTemperature(
                self.handle, pynvml.NVML_TEMPERATURE_GPU
            )

            # Get power usage (convert to watts)
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0
            except Exception:
                power = 0.0

            # Get memory info
            memory = pynvml.nvmlDeviceGetMemoryInfo(self.handle)

            # Get utilization rates
            utilization = pynvml.nvmlDeviceGetUtilizationRates(self.handle)

            # Get fan speed
            try:
                fan = pynvml.nvmlDeviceGetFanSpeed(self.handle)
            except Exception:
                fan = 0.0

            return {
                "name": name,
                "temperature": float(temp),
                "power_watts": float(power),
                "memory_total": memory.total,
                "memory_used": memory.used,
                "memory_free": memory.free,
                "gpu_utilization": float(utilization.gpu),
                "memory_utilization": float(utilization.memory),
                "fan_speed": float(fan),
            }
        except Exception as e:
            logger.error("Error collecting GPU metrics: %s", str(e))
            return {
                "name": "Error",
                "temperature": 0.0,
                "power_watts": 0.0,
                "memory_total": 0,
                "memory_used": 0,
                "memory_free": 0,
                "gpu_utilization": 0.0,
                "memory_utilization": 0.0,
                "fan_speed": 0.0,
            }

    # Alias for backward compatibility
    async def collect_metrics(self) -> dict[str, Union[int, float, str]]:
        """Alias for collect() method for backward compatibility.

        Returns:
            dict[str, Union[int, float, str]]: GPU metrics.
        """
        return await self.collect()
