"""Memory metrics collector module."""

import logging
from typing import Union

import psutil

from .base import BaseCollector

logger = logging.getLogger(__name__)


class MemoryCollector(BaseCollector):
    """Memory metrics collector.

    This collector gathers various memory metrics including:
    - Virtual memory (total, available, used, free, percentage)
    - Swap memory (total, used, free, percentage, swap in/out)
    """

    def __init__(self, interval: float = 1.0) -> None:
        """Initialize memory collector.

        Args:
            interval: Time interval in seconds for metric collection.
        """
        self.interval = interval

    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        return "memory"

    async def collect(self) -> dict[str, Union[int, float]]:
        """Collect memory metrics.

        Returns:
            dict[str, Union[int, float]]: Memory metrics for virtual and swap memory.
                Includes usage, capacity and performance statistics.
                Falls back to zeros if swap memory is unavailable.
        """
        # Get virtual memory metrics
        virtual = psutil.virtual_memory()
        metrics = {
            "total": virtual.total,
            "available": virtual.available,
            "used": virtual.used,
            "free": virtual.free,
            "percent": virtual.percent,
        }

        # Get swap memory metrics with fallback to zeros if not available
        try:
            swap = psutil.swap_memory()
            metrics.update(
                {
                    "swap_total": swap.total,
                    "swap_used": swap.used,
                    "swap_free": swap.free,
                    "swap_percent": swap.percent,
                    "swap_in": swap.sin,
                    "swap_out": swap.sout,
                }
            )
        except Exception as e:
            logger.warning("Failed to collect swap memory metrics: %s", e)
            metrics.update(
                {
                    "swap_total": 0,
                    "swap_used": 0,
                    "swap_free": 0,
                    "swap_percent": 0.0,
                    "swap_in": 0,
                    "swap_out": 0,
                }
            )

        return metrics
