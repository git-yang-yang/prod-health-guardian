"""Prometheus metrics module.

This module provides a simple interface for getting Prometheus metrics.
The actual collection and formatting is handled by the MetricsCollector class.
"""

from typing import Optional

from .collectors import MetricsCollector


class CollectorSingleton:
    """Singleton class for managing the metrics collector instance."""

    _instance: Optional[MetricsCollector] = None

    @classmethod
    def get_instance(cls) -> MetricsCollector:
        """Get or create the singleton metrics collector instance.

        Returns:
            MetricsCollector: The singleton metrics collector instance.
        """
        if cls._instance is None:
            cls._instance = MetricsCollector()
        return cls._instance


def get_collector() -> MetricsCollector:
    """Get or create the metrics collector.

    Returns:
        MetricsCollector: The metrics collector instance.
    """
    return CollectorSingleton.get_instance()


async def get_latest_metrics() -> bytes:
    """Get the latest metrics in Prometheus format.

    This function coordinates the collection and formatting of metrics
    into Prometheus format.

    Returns:
        bytes: Prometheus formatted metrics.
    """
    collector = get_collector()
    metrics = await collector.collect_metrics()
    collector.update_prometheus_metrics(metrics)
    return collector.get_prometheus_metrics()
