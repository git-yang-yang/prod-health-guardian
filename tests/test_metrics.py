"""Tests for the metrics module."""

from prod_health_guardian.metrics import get_basic_metrics


def test_get_basic_metrics() -> None:
    """Test that get_basic_metrics returns expected format and values.
    """
    metrics: dict[str, float] = get_basic_metrics()
    assert isinstance(metrics, dict)
    assert "test_metric" in metrics
    assert metrics["test_metric"] == 1.0
