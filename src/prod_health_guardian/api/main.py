"""Main API module."""

from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response

from prod_health_guardian import __version__
from prod_health_guardian.collectors.cpu import CPUCollector
from prod_health_guardian.collectors.memory import MemoryCollector
from prod_health_guardian.metrics import (
    get_latest_metrics,
    update_cpu_metrics,
    update_memory_metrics,
)
from prod_health_guardian.models import (
    CPUMetrics,
    ErrorResponse,
    HealthStatus,
    MemoryMetrics,
    SystemMetrics,
)

app = FastAPI(
    title="Production Health Guardian",
    description="A production health monitoring system",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Initialize collectors
cpu_collector = CPUCollector()
memory_collector = MemoryCollector()


@app.get(
    "/",
    tags=["System"],
    response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to API documentation"},
    }
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
    }
)
async def health_check() -> HealthStatus:
    """Health check endpoint.

    Returns:
        HealthStatus: Status of the service including version and system info.
    """
    return HealthStatus(
        status="healthy",
        version=__version__,
        system={
            "api": "running",
            "collectors": "ready"
        }
    )


@app.get(
    "/metrics",
    tags=["Metrics"],
    response_class=Response,
    responses={
        200: {
            "content": {"text/plain": {}},
            "description": "Prometheus formatted metrics"
        },
        500: {"model": ErrorResponse},
    }
)
async def get_metrics() -> Response:
    """Get metrics in Prometheus format.
    
    This is the standard Prometheus metrics endpoint that returns metrics
    in the Prometheus text-based format for scraping.

    Returns:
        Response: Prometheus formatted metrics.

    Raises:
        HTTPException: If metrics collection or formatting fails.
    """
    try:
        # Collect and validate metrics using models
        cpu_data = await cpu_collector.collect()
        memory_data = await memory_collector.collect()
        
        cpu_metrics = CPUMetrics(**cpu_data)
        memory_metrics = MemoryMetrics(**memory_data)
        
        # Update Prometheus metrics
        update_cpu_metrics(cpu_metrics.model_dump())
        update_memory_metrics(memory_metrics.model_dump())
        
        # Return metrics in Prometheus format
        return Response(
            content=get_latest_metrics(),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Prometheus metrics: {e!s}"
        ) from e


@app.get(
    "/metrics/json",
    tags=["Metrics"],
    response_model=SystemMetrics,
    responses={
        200: {"model": SystemMetrics},
        500: {"model": ErrorResponse},
    }
)
async def get_json_metrics() -> SystemMetrics:
    """Get system metrics in JSON format.

    Returns:
        SystemMetrics: Combined metrics from all collectors.

    Raises:
        HTTPException: If metrics collection fails.
    """
    try:
        cpu_data = await cpu_collector.collect()
        memory_data = await memory_collector.collect()
        
        return SystemMetrics(
            cpu=CPUMetrics(**cpu_data),
            memory=MemoryMetrics(**memory_data)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect metrics: {e!s}"
        ) from e


@app.get(
    "/metrics/json/{collector}",
    tags=["Metrics"],
    response_model=dict[str, Union[CPUMetrics, MemoryMetrics]],
    responses={
        200: {
            "model": dict[str, Union[CPUMetrics, MemoryMetrics]],
            "description": "Metrics from the specified collector"
        },
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def get_collector_metrics(
    collector: str
) -> dict[str, Union[CPUMetrics, MemoryMetrics]]:
    """Get metrics from a specific collector in JSON format.

    Args:
        collector: Name of the collector to get metrics from.

    Returns:
        dict[str, Union[CPUMetrics, MemoryMetrics]]: Metrics from the
            specified collector.

    Raises:
        HTTPException: If collector not found or metrics collection fails.
    """
    collectors = {
        "cpu": (cpu_collector, CPUMetrics),
        "memory": (memory_collector, MemoryMetrics),
    }
    
    if collector not in collectors:
        available = list(collectors.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Collector '{collector}' not found. Available: {available}"
        )
    
    try:
        collector_instance, model_class = collectors[collector]
        metrics = await collector_instance.collect()
        return {collector: model_class(**metrics)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect metrics from {collector}: {e!s}"
        ) from e
