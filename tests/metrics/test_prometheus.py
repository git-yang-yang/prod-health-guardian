"""Tests for the prometheus metrics module."""

from typing import TYPE_CHECKING

import pytest

from prod_health_guardian.metrics.prometheus import get_collector, get_latest_metrics

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_get_collector(mocker: "MockerFixture") -> None:
    """Test getting the global collector instance."""
    # First call should create a new instance
    collector1 = get_collector()
    assert collector1 is not None

    # Second call should return the same instance
    collector2 = get_collector()
    assert collector2 is collector1


@pytest.mark.asyncio
async def test_get_latest_metrics(mocker: "MockerFixture") -> None:
    """Test getting latest metrics in Prometheus format."""
    # Mock the collector methods
    collector = get_collector()
    mock_metrics = mocker.Mock()
    mock_prometheus_data = b"mock prometheus data"

    mocker.patch.object(
        collector,
        "collect_metrics",
        return_value=mock_metrics
    )
    mocker.patch.object(
        collector,
        "update_prometheus_metrics"
    )
    mocker.patch.object(
        collector,
        "get_prometheus_metrics",
        return_value=mock_prometheus_data
    )

    # Get metrics
    metrics = await get_latest_metrics()

    # Verify the flow
    collector.collect_metrics.assert_called_once()
    collector.update_prometheus_metrics.assert_called_once_with(mock_metrics)
    collector.get_prometheus_metrics.assert_called_once()
    assert metrics == mock_prometheus_data 