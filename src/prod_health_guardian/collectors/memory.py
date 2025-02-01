"""Memory metrics collector module."""

import psutil

from .base import BaseCollector


class MemoryCollector(BaseCollector):
    """Memory metrics collector.

    This collector gathers various memory metrics including:
    - Virtual memory (total, available, used, free, percentage)
    - Swap memory (total, used, free, percentage, swap in/out)
    """

    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        return "memory"

    async def collect(self) -> dict:
        """Collect memory metrics.

        Returns:
            dict: Memory metrics including virtual and swap memory information.
        """
        # Get virtual memory metrics
        virtual = psutil.virtual_memory()
        virtual_metrics = {
            "total": virtual.total,
            "available": virtual.available,
            "used": virtual.used,
            "free": virtual.free,
            "percent": virtual.percent,
        }

        # Get swap memory metrics
        swap = psutil.swap_memory()
        swap_metrics = {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent,
            "sin": swap.sin,
            "sout": swap.sout,
        }

        return {
            "virtual": virtual_metrics,
            "swap": swap_metrics,
        }
