"""Main API module."""

from typing import Any, Union

from fastapi import FastAPI, HTTPException

from prod_health_guardian import __version__
from prod_health_guardian.collectors.cpu import CPUCollector
from prod_health_guardian.collectors.memory import MemoryCollector

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


@app.get("/metrics", tags=["Metrics"])
async def get_metrics() -> dict[str, Any]:
    """Get system metrics from all collectors.

    Returns:
        dict[str, Any]: Combined metrics from all collectors.
    """
    cpu_metrics = await cpu_collector.collect()
    memory_metrics = await memory_collector.collect()
    
    return {
        cpu_collector.get_name(): cpu_metrics,
        memory_collector.get_name(): memory_metrics,
    }


@app.get("/metrics/{collector}", tags=["Metrics"])
async def get_collector_metrics(collector: str) -> dict[str, Any]:
    """Get metrics from a specific collector.

    Args:
        collector: Name of the collector to get metrics from.

    Returns:
        dict[str, Any]: Metrics from the specified collector.
    """
    collectors = {
        "cpu": cpu_collector,
        "memory": memory_collector,
    }
    
    if collector not in collectors:
        available = list(collectors.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Collector '{collector}' not found. Available: {available}"
        )
    
    metrics = await collectors[collector].collect()
    return {collector: metrics}
