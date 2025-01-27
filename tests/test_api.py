"""Tests for the API endpoints."""

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from prod_health_guardian import __version__
from prod_health_guardian.api.main import app

if TYPE_CHECKING:
    pass  # No type-only imports needed

# HTTP Status Codes
HTTP_200_OK = 200


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API.

    Returns:
        TestClient: FastAPI test client.
    """
    return TestClient(app)


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
