"""Memory metrics collector module."""

import logging

import psutil

from .base import BaseCollector

logger = logging.getLogger(__name__)


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
                If swap memory is not available, returns zeros for swap metrics.
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

        # Get swap memory metrics with fallback to zeros if not available
        try:
            swap = psutil.swap_memory()
            swap_metrics = {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent,
                "sin": swap.sin,
                "sout": swap.sout,
            }
        except Exception as e:
            logger.warning("Failed to collect swap memory metrics: %s", e)
            swap_metrics = {
                "total": 0,
                "used": 0,
                "free": 0,
                "percent": 0.0,
                "sin": 0,
                "sout": 0,
            }

        return {
            "virtual": virtual_metrics,
            "swap": swap_metrics,
        }
