"""Common test fixtures and configuration."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from prod_health_guardian.api.main import app

if TYPE_CHECKING:
    pass

# Test constants
MEMORY_VIRTUAL_TOTAL = 16_000_000_000  # 16GB


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API.

    Returns:
        TestClient: FastAPI test client.
    """
    return TestClient(app)


@pytest.fixture
async def clear_collectors() -> AsyncGenerator[None, None]:
    """Clear all collectors after each test.

    This prevents state from leaking between tests.

    Yields:
        None: No value is yielded.
    """
    yield
    # Reset any collector state here if needed
