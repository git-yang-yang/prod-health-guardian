"""Prometheus metrics exporter."""

from typing import Any

from prometheus_client import Gauge, generate_latest

# CPU Metrics
cpu_physical_count = Gauge(
    "cpu_physical_count",
    "Number of physical CPU cores"
)

cpu_logical_count = Gauge(
    "cpu_logical_count",
    "Number of logical CPU cores"
)

cpu_frequency_current = Gauge(
    "cpu_frequency_current_mhz",
    "Current CPU frequency in MHz"
)

cpu_frequency_min = Gauge(
    "cpu_frequency_min_mhz",
    "Minimum CPU frequency in MHz"
)

cpu_frequency_max = Gauge(
    "cpu_frequency_max_mhz",
    "Maximum CPU frequency in MHz"
)

cpu_percent_total = Gauge(
    "cpu_percent_total",
    "Total CPU usage percentage"
)

cpu_percent_per_cpu = Gauge(
    "cpu_percent_per_cpu",
    "CPU usage percentage per core",
    ["core"]
)

cpu_ctx_switches = Gauge(
    "cpu_ctx_switches_total",
    "Total number of context switches"
)

cpu_interrupts = Gauge(
    "cpu_interrupts_total",
    "Total number of interrupts"
)

cpu_soft_interrupts = Gauge(
    "cpu_soft_interrupts_total",
    "Total number of soft interrupts"
)

cpu_syscalls = Gauge(
    "cpu_syscalls_total",
    "Total number of system calls"
)

# Memory Metrics
memory_virtual_total = Gauge(
    "memory_virtual_total_bytes",
    "Total virtual memory in bytes"
)

memory_virtual_available = Gauge(
    "memory_virtual_available_bytes",
    "Available virtual memory in bytes"
)

memory_virtual_used = Gauge(
    "memory_virtual_used_bytes",
    "Used virtual memory in bytes"
)

memory_virtual_free = Gauge(
    "memory_virtual_free_bytes",
    "Free virtual memory in bytes"
)

memory_virtual_percent = Gauge(
    "memory_virtual_percent",
    "Virtual memory usage percentage"
)

memory_swap_total = Gauge(
    "memory_swap_total_bytes",
    "Total swap memory in bytes"
)

memory_swap_used = Gauge(
    "memory_swap_used_bytes",
    "Used swap memory in bytes"
)

memory_swap_free = Gauge(
    "memory_swap_free_bytes",
    "Free swap memory in bytes"
)

memory_swap_percent = Gauge(
    "memory_swap_percent",
    "Swap memory usage percentage"
)

memory_swap_sin = Gauge(
    "memory_swap_sin_total",
    "Total number of memory pages swapped in"
)

memory_swap_sout = Gauge(
    "memory_swap_sout_total",
    "Total number of memory pages swapped out"
)


def update_cpu_metrics(metrics: dict[str, Any]) -> None:
    """Update CPU metrics in Prometheus format.

    Args:
        metrics: CPU metrics data.
    """
    # Update core counts
    cpu_physical_count.set(metrics["count"]["physical"])
    cpu_logical_count.set(metrics["count"]["logical"])

    # Update frequencies
    if metrics["frequency"]["current"] is not None:
        cpu_frequency_current.set(metrics["frequency"]["current"])
    if metrics["frequency"]["min"] is not None:
        cpu_frequency_min.set(metrics["frequency"]["min"])
    if metrics["frequency"]["max"] is not None:
        cpu_frequency_max.set(metrics["frequency"]["max"])

    # Update usage percentages
    cpu_percent_total.set(metrics["percent"]["total"])
    for i, percent in enumerate(metrics["percent"]["per_cpu"]):
        cpu_percent_per_cpu.labels(core=str(i)).set(percent)

    # Update stats
    cpu_ctx_switches.set(metrics["stats"]["ctx_switches"])
    cpu_interrupts.set(metrics["stats"]["interrupts"])
    cpu_soft_interrupts.set(metrics["stats"]["soft_interrupts"])
    cpu_syscalls.set(metrics["stats"]["syscalls"])


def update_memory_metrics(metrics: dict[str, Any]) -> None:
    """Update memory metrics in Prometheus format.

    Args:
        metrics: Memory metrics data.
    """
    # Update virtual memory metrics
    memory_virtual_total.set(metrics["virtual"]["total"])
    memory_virtual_available.set(metrics["virtual"]["available"])
    memory_virtual_used.set(metrics["virtual"]["used"])
    memory_virtual_free.set(metrics["virtual"]["free"])
    memory_virtual_percent.set(metrics["virtual"]["percent"])

    # Update swap memory metrics
    memory_swap_total.set(metrics["swap"]["total"])
    memory_swap_used.set(metrics["swap"]["used"])
    memory_swap_free.set(metrics["swap"]["free"])
    memory_swap_percent.set(metrics["swap"]["percent"])
    memory_swap_sin.set(metrics["swap"]["sin"])
    memory_swap_sout.set(metrics["swap"]["sout"])


def get_latest_metrics() -> bytes:
    """Get latest metrics in Prometheus format.

    Returns:
        bytes: Prometheus formatted metrics.
    """
    return generate_latest() 