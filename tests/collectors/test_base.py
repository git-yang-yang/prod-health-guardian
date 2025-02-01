"""Tests for hardware metric collectors.

This module contains integration tests for all collectors and tests for
the base collector. Detailed tests for each collector are in the
collectors/ directory.
"""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors import (
    BaseCollector,
    CPUCollector,
    GPUCollector,
    MemoryCollector,
)

if TYPE_CHECKING:
    pass


class TestCollector(BaseCollector):
    """Test collector implementation."""

    interval: float = 1.0

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
        return {"test_value": 42}


@pytest.mark.asyncio
async def test_base_collector() -> None:
    """Test base collector functionality."""
    collector = TestCollector()
    assert collector.get_name() == "test"
    assert collector.is_available is True

    metrics = await collector.collect()
    assert metrics == {"test_value": 42}


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
        metrics = await collector.collect()
        assert isinstance(metrics, dict)
        assert all(isinstance(key, str) for key in metrics.keys())
        assert all(
            isinstance(value, (int, float, str, list)) for value in metrics.values()
        )
