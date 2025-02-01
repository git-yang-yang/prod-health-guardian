"""CPU metrics collector module."""

import psutil

from .base import BaseCollector


class CPUCollector(BaseCollector):
    """CPU metrics collector.

    This collector gathers various CPU metrics including:
    - Core counts (physical and logical)
    - CPU frequencies (current, min, max)
    - CPU usage percentages (total and per-core)
    - CPU statistics (context switches, interrupts, etc.)

    Args:
        interval: Time interval in seconds for CPU percentage calculation.
            Defaults to 0.1 seconds.
    """

    def __init__(self, interval: float = 0.1) -> None:
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

    async def collect(self) -> dict:
        """Collect CPU metrics.

        Returns:
            dict: CPU metrics including core counts, frequencies,
                usage percentages, and statistics.
        """
        # Get CPU counts
        cpu_count = {
            "physical": psutil.cpu_count(logical=False),
            "logical": psutil.cpu_count(logical=True),
        }

        # Get CPU frequencies
        cpu_freq = psutil.cpu_freq()
        frequencies = {
            "current": float(cpu_freq.current) if cpu_freq else None,
            "min": float(cpu_freq.min) if cpu_freq else None,
            "max": float(cpu_freq.max) if cpu_freq else None,
        }

        # Get CPU usage percentages
        cpu_percent = {
            "total": psutil.cpu_percent(interval=self.interval),
            "per_cpu": psutil.cpu_percent(interval=self.interval, percpu=True),
        }

        # Get CPU statistics
        cpu_stats = psutil.cpu_stats()
        stats = {
            "ctx_switches": cpu_stats.ctx_switches,
            "interrupts": cpu_stats.interrupts,
            "soft_interrupts": cpu_stats.soft_interrupts,
            "syscalls": cpu_stats.syscalls,
        }

        return {
            "count": cpu_count,
            "frequency": frequencies,
            "percent": cpu_percent,
            "stats": stats,
        }
