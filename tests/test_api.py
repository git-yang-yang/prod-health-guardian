"""Tests for the API endpoints."""

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from prod_health_guardian import __version__
from prod_health_guardian.api.main import app

if TYPE_CHECKING:
    pass  # No type-only imports needed

# HTTP Status Codes
HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404


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
    assert "count" in cpu
    assert "frequency" in cpu
    assert "percent" in cpu
    assert "stats" in cpu
    
    # Check memory metrics structure
    memory = data["memory"]
    assert "virtual" in memory
    assert "swap" in memory


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
    assert "count" in cpu
    assert "frequency" in cpu
    assert "percent" in cpu
    assert "stats" in cpu


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
    assert "virtual" in memory
    assert "swap" in memory


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
