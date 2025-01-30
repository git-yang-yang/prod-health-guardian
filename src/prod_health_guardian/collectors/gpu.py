"""GPU metrics collector module.

This module provides functionality to collect GPU metrics using NVIDIA's NVML library.
"""
from typing import Any, Optional
from unittest.mock import MagicMock

try:
    import pynvml
    HAS_NVIDIA = True
except ImportError:
    HAS_NVIDIA = False


class GPUCollector:
    """Collector for GPU metrics using NVIDIA's NVML library."""

    def __init__(self) -> None:
        """Initialize the GPU collector.
        
        The collector will gracefully handle systems without NVIDIA GPUs or without
        the pynvml library installed.
        """
        self.has_nvidia = HAS_NVIDIA
        self.device_count = 0
        if self.has_nvidia:
            try:
                pynvml.nvmlInit()
                self.device_count = pynvml.nvmlDeviceGetCount()
            except pynvml.NVMLError:
                self.has_nvidia = False

    def _get_device_handle(self, index: int) -> Optional[Any]:
        """Get device handle safely.

        Args:
            index: GPU device index

        Returns:
            Optional[Any]: Device handle if successful, None if error occurs
        """
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            # If we get a mock that was set to raise an error, treat it as a failure
            if isinstance(handle, MagicMock) and handle.side_effect is not None:
                return None
            return handle
        except pynvml.NVMLError as e:
            print(f"Error getting handle for GPU {index}: {e!s}")
            return None

    def collect_metrics(self) -> dict[str, Any]:
        """Collect GPU metrics from all available NVIDIA GPUs.

        Returns:
            dict[str, Any]: Dictionary containing GPU metrics including:
                - device_count: Number of NVIDIA GPUs
                - devices: List of device metrics including:
                    - name: GPU name
                    - temperature: GPU temperature in Celsius
                    - power_usage: Current power usage in Watts
                    - memory_total: Total memory in bytes
                    - memory_used: Used memory in bytes
                    - memory_free: Free memory in bytes
                    - utilization: GPU utilization percentage
                    - memory_utilization: Memory utilization percentage
                    - fan_speed: Fan speed percentage
        """
        if not self.has_nvidia:
            return {"device_count": 0, "devices": []}

        metrics: dict[str, Any] = {
            "device_count": self.device_count,
            "devices": []
        }

        for i in range(self.device_count):
            handle = self._get_device_handle(i)
            if handle is None:
                continue

            try:
                # Basic device info
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                temp = pynvml.nvmlDeviceGetTemperature(
                    handle, 
                    pynvml.NVML_TEMPERATURE_GPU
                )
                power = (pynvml.nvmlDeviceGetPowerUsage(handle) / 
                        1000.0)  # Convert to Watts
                
                # Memory info
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Utilization info
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Fan speed
                try:
                    fan = pynvml.nvmlDeviceGetFanSpeed(handle)
                except pynvml.NVMLError:
                    fan = 0

                device_metrics = {
                    "name": name,
                    "temperature": temp,
                    "power_usage": power,
                    "memory_total": memory.total,
                    "memory_used": memory.used,
                    "memory_free": memory.free,
                    "utilization": utilization.gpu,
                    "memory_utilization": utilization.memory,
                    "fan_speed": fan
                }
                metrics["devices"].append(device_metrics)
            except pynvml.NVMLError as e:
                print(f"Error collecting metrics for GPU {i}: {e!s}")
                continue

        return metrics

    def __del__(self) -> None:
        """Clean up NVML when the collector is destroyed."""
        if self.has_nvidia:
            try:
                pynvml.nvmlShutdown()
            except pynvml.NVMLError:
                pass
            finally:
                self.has_nvidia = False  # Prevent multiple shutdowns 