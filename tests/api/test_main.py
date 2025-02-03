"""Tests for the API endpoints."""

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from prod_health_guardian import __version__
from prod_health_guardian.api.main import app

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

# HTTP Status Codes
HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the API.

    Returns:
        TestClient: FastAPI test client.
    """
    with TestClient(app) as client:
        yield client


@pytest.mark.system
def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint.

    Args:
        client: FastAPI test client.
    """
    response = client.get("/health")
    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == __version__
    assert "system" in data
    assert data["system"]["api"] == "running"
    assert data["system"]["collectors"] == "ready"


def test_get_metrics(client: TestClient) -> None:
    """Test the Prometheus metrics endpoint.

    Args:
        client: FastAPI test client.
    """
    response = client.get("/metrics")
    assert response.status_code == HTTP_200_OK
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

    # Verify that the response can be parsed as Prometheus metrics
    metrics = list(text_string_to_metric_families(response.text))
    assert len(metrics) > 0

    # Check for presence of key metrics
    metric_names = {m.name for m in metrics}
    assert "cpu_physical_count" in metric_names
    assert "cpu_logical_count" in metric_names
    assert "cpu_frequency_current_mhz" in metric_names
    assert "memory_virtual_total_bytes" in metric_names
    assert "memory_swap_total_bytes" in metric_names


def test_get_metrics_error(client: TestClient, mocker: "MockerFixture") -> None:
    """Test error handling in the metrics endpoint.

    Args:
        client: FastAPI test client.
        mocker: Pytest mocker fixture.
    """
    # Mock CPU collector to raise an exception
    mocker.patch(
        "prod_health_guardian.collectors.cpu.CPUCollector.collect",
        side_effect=Exception("Test error"),
    )

    response = client.get("/metrics")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Failed to generate Prometheus metrics: Test error"


def test_get_json_metrics(client: TestClient) -> None:
    """Test the JSON metrics endpoint.

    Args:
        client: FastAPI test client.
    """
    response = client.get("/metrics/json")
    assert response.status_code == HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "cpu" in data
    assert "memory" in data

    # Check CPU metrics structure
    cpu = data["cpu"]
    assert "physical_cores" in cpu
    assert "logical_cores" in cpu
    assert "cpu_freq_current" in cpu
    assert "cpu_freq_min" in cpu
    assert "cpu_freq_max" in cpu
    assert "cpu_percent" in cpu
    assert "per_cpu_percent" in cpu


def test_get_json_metrics_error(client: TestClient, mocker: "MockerFixture") -> None:
    """Test error handling in the JSON metrics endpoint.

    Args:
        client: FastAPI test client.
        mocker: Pytest mocker fixture.
    """
    # Mock memory collector to raise an exception
    mocker.patch(
        "prod_health_guardian.collectors.memory.MemoryCollector.collect",
        side_effect=Exception("Test error"),
    )

    response = client.get("/metrics/json")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "detail" in data
    assert "Failed to collect metrics" in data["detail"]
    assert "Test error" in data["detail"]


def test_get_cpu_metrics(client: TestClient) -> None:
    """Test getting CPU metrics in JSON format.

    Args:
        client: FastAPI test client.
    """
    response = client.get("/metrics/json/cpu")
    assert response.status_code == HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "cpu" in data
    cpu = data["cpu"]
    assert "physical_cores" in cpu
    assert "logical_cores" in cpu
    assert "cpu_freq_current" in cpu
    assert "cpu_freq_min" in cpu
    assert "cpu_freq_max" in cpu
    assert "cpu_percent" in cpu
    assert "per_cpu_percent" in cpu


def test_get_memory_metrics(client: TestClient) -> None:
    """Test getting memory metrics in JSON format.

    Args:
        client: FastAPI test client.
    """
    response = client.get("/metrics/json/memory")
    assert response.status_code == HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "memory" in data
    memory = data["memory"]
    assert "total" in memory
    assert "available" in memory
    assert "used" in memory
    assert "free" in memory
    assert "percent" in memory
    assert "swap_total" in memory
    assert "swap_used" in memory
    assert "swap_free" in memory
    assert "swap_percent" in memory


def test_get_collector_metrics_error(
    client: TestClient,
    mocker: "MockerFixture",
) -> None:
    """Test error handling in the collector metrics endpoint.

    Args:
        client: FastAPI test client.
        mocker: Pytest mocker fixture.
    """
    # Mock CPU collector to raise an exception
    mocker.patch(
        "prod_health_guardian.collectors.cpu.CPUCollector.collect",
        side_effect=Exception("Test error"),
    )

    response = client.get("/metrics/json/cpu")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Failed to collect metrics from cpu"


def test_get_invalid_collector_metrics(client: TestClient) -> None:
    """Test getting metrics from an invalid collector.

    Args:
        client: FastAPI test client.
    """
    response = client.get("/metrics/json/invalid")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "detail" in data
