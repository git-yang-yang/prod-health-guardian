"""Tests for hardware metric collectors."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.collectors.base import MetricCollector
from prod_health_guardian.collectors.cpu import CPUCollector
from prod_health_guardian.collectors.gpu import GPUCollector
from prod_health_guardian.collectors.memory import MemoryCollector

if TYPE_CHECKING:
    pass  # No type-only imports needed


class TestCollector(MetricCollector):
    """Test implementation of MetricCollector."""

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
async def test_cpu_collector_basic() -> None:
    """Basic integration test for CPU collector.
    
    Note: Detailed CPU tests are in tests/collectors/test_cpu.py
    """
    collector = CPUCollector()
    metrics = await collector.collect()
    
    # Check basic structure only
    assert isinstance(metrics, dict)
    assert "count" in metrics
    assert "frequency" in metrics
    assert "percent" in metrics
    assert "stats" in metrics


@pytest.mark.collectors
@pytest.mark.asyncio
async def test_memory_collector_basic() -> None:
    """Basic integration test for Memory collector.
    
    Note: Detailed Memory tests are in tests/collectors/test_memory.py
    """
    collector = MemoryCollector()
    metrics = await collector.collect()
    
    # Check basic structure only
    assert isinstance(metrics, dict)
    assert "virtual" in metrics
    assert "swap" in metrics


@pytest.mark.collectors
def test_gpu_collector_basic() -> None:
    """Basic integration test for GPU collector.
    
    Note: Detailed GPU tests are in tests/collectors/test_gpu.py
    """
    collector = GPUCollector()
    metrics = collector.collect_metrics()
    
    # Check basic structure only
    assert isinstance(metrics, dict)
    assert "device_count" in metrics
    assert "devices" in metrics
    assert isinstance(metrics["device_count"], int)
    assert isinstance(metrics["devices"], list) 