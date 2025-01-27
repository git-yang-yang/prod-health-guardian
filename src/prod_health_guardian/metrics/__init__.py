"""Metrics package."""

from prod_health_guardian.metrics.prometheus import (
    get_latest_metrics,
    update_cpu_metrics,
    update_memory_metrics,
)

__all__ = ["get_latest_metrics", "update_cpu_metrics", "update_memory_metrics"] 