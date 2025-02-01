"""Metrics package."""

from prod_health_guardian.metrics.collectors import MetricsCollector
from prod_health_guardian.metrics.prometheus import get_collector, get_latest_metrics

__all__ = [
    "MetricsCollector",
    "get_collector",
    "get_latest_metrics",
]
