"""Main API module."""

from typing import Union

from fastapi import FastAPI

from prod_health_guardian import __version__

app = FastAPI(
    title="Production Health Guardian",
    description="A production health monitoring system",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, Union[str, dict[str, str]]]:
    """Health check endpoint.

    Returns:
        dict[str, Union[str, dict[str, str]]]: Status of the service including version
            and system info.
    """
    return {
        "status": "healthy",
        "version": __version__,
        "system": {
            "api": "running",
            "collectors": "ready"
        }
    }
