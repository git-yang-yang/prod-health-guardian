"""Tests for hardware metric collectors.

This module contains integration tests for all collectors and tests for
the base collector. Detailed tests for each collector are in the
collectors/ directory.
"""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors.base import BaseCollector
from prod_health_guardian.collectors.cpu import CPUCollector
from prod_health_guardian.collectors.gpu import GPUCollector
from prod_health_guardian.collectors.memory import MemoryCollector

if TYPE_CHECKING:
    pass  # No type-only imports needed


class TestCollector(BaseCollector):
    """Test implementation of BaseCollector."""

    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        return "test"

    async def collect(self) -> dict[str, int]:
        """Collect test metrics.

        Returns:
            dict[str, int]: Test metrics.
        """
        return {"value": 42}


def test_base_collector() -> None:
    """Test base collector functionality."""
    collector = TestCollector()
    assert collector.get_name() == "test"
    assert collector.is_available is True


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_collector_integration() -> None:
    """Integration test for all collectors working together.

    This test ensures that all collectors can be instantiated and used together,
    which is important for the metrics collection system as a whole.
    """
    # Test all collectors can be instantiated and collect metrics
    collectors = [
        CPUCollector(),
        MemoryCollector(),
        GPUCollector(),
    ]

    for collector in collectors:
        if isinstance(collector, GPUCollector):
            metrics = collector.collect_metrics()
        else:
            metrics = await collector.collect()

        # Basic validation that metrics are returned
        assert isinstance(metrics, dict)
        assert len(metrics) > 0

        # Validate that all values in the metrics dict are of expected types
        def validate_dict_types(d: dict) -> None:
            for v in d.values():
                if isinstance(v, dict):
                    validate_dict_types(v)
                elif isinstance(v, list):
                    assert all(
                        isinstance(x, (int, float, str, bool, type(None))) for x in v
                    )
                else:
                    assert isinstance(v, (int, float, str, bool, type(None)))

        validate_dict_types(metrics)
