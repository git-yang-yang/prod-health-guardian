"""CPU metrics collector."""

from typing import Any

import psutil

from prod_health_guardian.collectors.base import MetricCollector


class CPUCollector(MetricCollector):
    """Collector for CPU metrics."""

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

    async def collect(self) -> dict[str, Any]:
        """Collect CPU metrics.

        Returns:
            dict[str, Any]: CPU metrics including usage percentages and count.
        """
        # Get CPU count
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)

        # Get CPU frequency
        freq = psutil.cpu_freq()
        freq_data = {
            "current": float(freq.current) if freq else None,
            "min": float(freq.min) if freq and freq.min else None,
            "max": float(freq.max) if freq and freq.max else None
        }

        # Get CPU usage (requires sleep)
        cpu_percent = psutil.cpu_percent(interval=self.interval)
        per_cpu = psutil.cpu_percent(interval=0, percpu=True)

        # Get CPU stats
        stats = psutil.cpu_stats()
        stats_data = {
            "ctx_switches": stats.ctx_switches,
            "interrupts": stats.interrupts,
            "soft_interrupts": stats.soft_interrupts,
            "syscalls": stats.syscalls
        }

        return {
            "count": {
                "physical": cpu_count,
                "logical": cpu_count_logical
            },
            "frequency": freq_data,
            "percent": {
                "total": cpu_percent,
                "per_cpu": per_cpu
            },
            "stats": stats_data
        } 