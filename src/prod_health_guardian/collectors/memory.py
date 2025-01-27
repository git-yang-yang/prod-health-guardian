"""Memory metrics collector."""

from typing import Any

import psutil

from prod_health_guardian.collectors.base import MetricCollector


class MemoryCollector(MetricCollector):
    """Collector for memory metrics."""

    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        return "memory"

    async def collect(self) -> dict[str, Any]:
        """Collect memory metrics.

        Returns:
            dict[str, Any]: Memory metrics including virtual and swap memory.
        """
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "virtual": {
                "total": virtual.total,
                "available": virtual.available,
                "used": virtual.used,
                "free": virtual.free,
                "percent": virtual.percent,
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent,
                "sin": swap.sin,
                "sout": swap.sout,
            }
        } 