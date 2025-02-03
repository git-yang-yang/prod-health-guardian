"""Main API module."""

from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response

from prod_health_guardian import __version__
from prod_health_guardian.collectors.cpu import CPUCollector
from prod_health_guardian.collectors.memory import MemoryCollector
from prod_health_guardian.metrics import (
    get_collector,
    get_latest_metrics,
)
from prod_health_guardian.models import (
    CPUMetrics,
    ErrorResponse,
    GPUMetrics,
    HealthStatus,
    MemoryMetrics,
)

app = FastAPI(
    title="Production Health Guardian",
    description="API for monitoring system health and metrics",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Initialize collectors
cpu_collector = CPUCollector()
memory_collector = MemoryCollector()

# Initialize metrics collector
metrics_collector = get_collector()


@app.get(
    "/",
    tags=["System"],
    response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to API documentation"},
    },
)
async def root() -> RedirectResponse:
    """Root endpoint that redirects to API documentation.

    Returns:
        RedirectResponse: Redirect to the API documentation.
    """
    return RedirectResponse(url="/api/docs")


@app.get(
    "/health",
    tags=["System"],
    response_model=HealthStatus,
    responses={
        200: {"model": HealthStatus},
    },
)
async def health_check() -> HealthStatus:
    """Health check endpoint.

    Returns:
        HealthStatus: Status of the service including version and system info.
    """
    try:
        # Try to collect metrics from all collectors
        await cpu_collector.collect()
        await memory_collector.collect()

        return HealthStatus(
            status="healthy",
            version=__version__,
            system={
                "api": "running",
                "collectors": "ready",
            },
        )
    except Exception as e:
        return HealthStatus(
            status="unhealthy",
            error=f"{e!s}",
        )


@app.get(
    "/metrics",
    tags=["Metrics"],
    response_class=Response,
    responses={
        200: {
            "content": {"text/plain": {}},
            "description": "Prometheus formatted metrics",
        },
        500: {"model": ErrorResponse},
    },
)
async def get_metrics() -> Response:
    """Get system metrics in Prometheus format.

    This endpoint returns all system metrics in Prometheus text format,
    suitable for scraping by Prometheus.

    Returns:
        Response: Prometheus formatted metrics

    Raises:
        HTTPException: If metrics collection fails
    """
    try:
        # Get metrics in Prometheus format
        metrics = await get_latest_metrics()
        return Response(
            content=metrics,
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Prometheus metrics: {e!s}",
        ) from e


@app.get(
    "/metrics/json",
    tags=["Metrics"],
    response_model=dict[str, Union[CPUMetrics, MemoryMetrics, GPUMetrics]],
    responses={
        200: {"model": dict[str, Union[CPUMetrics, MemoryMetrics, GPUMetrics]]},
        500: {"model": ErrorResponse},
    },
)
async def get_json_metrics() -> dict[str, Union[CPUMetrics, MemoryMetrics, GPUMetrics]]:
    """Get system metrics in JSON format.

    This endpoint returns all system metrics in a structured JSON format,
    validated through Pydantic models.

    Returns:
        dict: Combined system metrics

    Raises:
        HTTPException: If metrics collection fails
    """
    try:
        metrics = await metrics_collector.collect_metrics()
        return {
            "cpu": metrics.cpu,
            "memory": metrics.memory,
            "gpu": metrics.gpu,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect metrics: {e!s}",
        ) from e


@app.get(
    "/metrics/json/{collector}",
    tags=["Metrics"],
    response_model=dict[str, Union[CPUMetrics, MemoryMetrics]],
    responses={
        200: {
            "model": dict[str, Union[CPUMetrics, MemoryMetrics]],
            "description": "Metrics from the specified collector",
        },
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_collector_metrics(
    collector: str,
) -> dict[str, Union[CPUMetrics, MemoryMetrics]]:
    """Get metrics from a specific collector.

    This endpoint returns metrics from a single collector in JSON format.

    Args:
        collector: Name of the collector (cpu or memory)

    Returns:
        dict: Collector metrics

    Raises:
        HTTPException: If collector doesn't exist or metrics collection fails
    """
    try:
        if collector == "cpu":
            data = await cpu_collector.collect()
            return {"cpu": CPUMetrics(**data)}
        elif collector == "memory":
            data = await memory_collector.collect()
            return {"memory": MemoryMetrics(**data)}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Collector '{collector}' not found",
            )
    except HTTPException as e:
        raise e from None
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect metrics from {collector}",
        ) from e
