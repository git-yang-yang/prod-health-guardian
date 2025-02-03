"""CPU metrics collector module."""

from typing import Union

import psutil

from .base import BaseCollector


class CPUCollector(BaseCollector):
    """CPU metrics collector.

    This collector gathers various CPU metrics including:
    - Core counts (physical and logical)
    - CPU frequencies (current, min, max)
    - CPU usage percentages (total and per-core)
    - CPU statistics (context switches, interrupts, etc.)
    """

    def __init__(self, interval: float = 1.0) -> None:
        """Initialize CPU collector.

        Args:
            interval: Time interval in seconds for CPU percentage calculation.
        """
        self.interval = interval

    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        return "cpu"

    async def collect(self) -> dict[str, Union[int, float, list[float]]]:
        """Collect CPU metrics.

        Returns:
            dict[str, Union[int, float, list[float]]]: Dictionary of CPU metrics.
                Contains core counts, frequencies, usage percentages, and stats.
        """
        # Get CPU counts
        metrics = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
        }

        # Get CPU frequencies
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            metrics["cpu_freq_current"] = float(cpu_freq.current)
            metrics["cpu_freq_min"] = float(cpu_freq.min)
            metrics["cpu_freq_max"] = float(cpu_freq.max)
        else:
            metrics["cpu_freq_current"] = 0.0
            metrics["cpu_freq_min"] = 0.0
            metrics["cpu_freq_max"] = 0.0

        # Get CPU usage percentages
        metrics["cpu_percent"] = psutil.cpu_percent(interval=self.interval)
        metrics["per_cpu_percent"] = psutil.cpu_percent(
            interval=self.interval, percpu=True
        )

        # Get CPU statistics
        cpu_stats = psutil.cpu_stats()
        metrics["ctx_switches"] = cpu_stats.ctx_switches
        metrics["interrupts"] = cpu_stats.interrupts
        metrics["soft_interrupts"] = cpu_stats.soft_interrupts
        metrics["syscalls"] = cpu_stats.syscalls

        return metrics
