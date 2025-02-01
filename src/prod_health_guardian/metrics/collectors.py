"""Metrics collector coordination module."""

from prometheus_client import Gauge, generate_latest

from ..collectors.cpu import CPUCollector
from ..collectors.gpu import GPUCollector
from ..collectors.memory import MemoryCollector
from ..models.metrics import CPUMetrics, GPUMetrics, MemoryMetrics, SystemMetrics


class MetricsCollector:
    """Single entry point for all metrics collection and export.

    This class serves as the main coordinator for all metrics collection,
    formatting, and export. It handles both the collection of raw metrics
    and their conversion to various formats (e.g., Prometheus).

    The collector follows a unified pattern where:
    1. Raw metrics are collected from hardware collectors
    2. Metrics are validated through Pydantic models
    3. Metrics can be exported in different formats

    It also implements the Prometheus collector interface for custom collectors,
    allowing direct registration with the Prometheus registry.
    """

    def __init__(self) -> None:
        """Initialize metrics collector with hardware collectors and metrics."""
        # Initialize collectors
        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.gpu_collector = GPUCollector()

        # Register Prometheus metrics
        self._register_metrics()

    def _register_metrics(self) -> None:
        """Register all Prometheus metrics.

        This method initializes all the Prometheus gauge metrics that will
        be used to export metrics in Prometheus format.
        """
        # CPU Metrics
        self.cpu_physical_count = Gauge(
            "cpu_physical_count",
            "Number of physical CPU cores",
        )
        self.cpu_logical_count = Gauge(
            "cpu_logical_count",
            "Number of logical CPU cores",
        )
        self.cpu_frequency_current = Gauge(
            "cpu_frequency_current_mhz",
            "Current CPU frequency in MHz",
        )
        self.cpu_frequency_min = Gauge(
            "cpu_frequency_min_mhz",
            "Minimum CPU frequency in MHz",
        )
        self.cpu_frequency_max = Gauge(
            "cpu_frequency_max_mhz",
            "Maximum CPU frequency in MHz",
        )
        self.cpu_percent_total = Gauge(
            "cpu_percent_total",
            "Total CPU usage percentage",
        )
        self.cpu_percent_per_cpu = Gauge(
            "cpu_percent_per_cpu",
            "CPU usage percentage per core",
            ["core"],
        )
        self.cpu_ctx_switches = Gauge(
            "cpu_ctx_switches_total",
            "Total number of context switches",
        )
        self.cpu_interrupts = Gauge(
            "cpu_interrupts_total",
            "Total number of interrupts",
        )
        self.cpu_soft_interrupts = Gauge(
            "cpu_soft_interrupts_total",
            "Total number of soft interrupts",
        )
        self.cpu_syscalls = Gauge(
            "cpu_syscalls_total",
            "Total number of system calls",
        )

        # Memory Metrics
        self.memory_virtual_total = Gauge(
            "memory_virtual_total_bytes",
            "Total virtual memory in bytes",
        )
        self.memory_virtual_available = Gauge(
            "memory_virtual_available_bytes",
            "Available virtual memory in bytes",
        )
        self.memory_virtual_used = Gauge(
            "memory_virtual_used_bytes",
            "Used virtual memory in bytes",
        )
        self.memory_virtual_free = Gauge(
            "memory_virtual_free_bytes",
            "Free virtual memory in bytes",
        )
        self.memory_virtual_percent = Gauge(
            "memory_virtual_percent",
            "Virtual memory usage percentage",
        )
        self.memory_swap_total = Gauge(
            "memory_swap_total_bytes",
            "Total swap memory in bytes",
        )
        self.memory_swap_used = Gauge(
            "memory_swap_used_bytes",
            "Used swap memory in bytes",
        )
        self.memory_swap_free = Gauge(
            "memory_swap_free_bytes",
            "Free swap memory in bytes",
        )
        self.memory_swap_percent = Gauge(
            "memory_swap_percent",
            "Swap memory usage percentage",
        )
        self.memory_swap_sin = Gauge(
            "memory_swap_sin_total",
            "Total number of memory pages swapped in",
        )
        self.memory_swap_sout = Gauge(
            "memory_swap_sout_total",
            "Total number of memory pages swapped out",
        )

        # GPU Metrics
        self.gpu_device_count = Gauge(
            "gpu_device_count",
            "Number of NVIDIA GPUs available",
        )
        self.gpu_temperature = Gauge(
            "gpu_temperature_celsius",
            "GPU temperature in Celsius",
            ["gpu_id", "name"],
        )
        self.gpu_power = Gauge(
            "gpu_power_watts",
            "GPU power usage in Watts",
            ["gpu_id", "name"],
        )
        self.gpu_memory_total = Gauge(
            "gpu_memory_total_bytes",
            "Total GPU memory in bytes",
            ["gpu_id", "name"],
        )
        self.gpu_memory_used = Gauge(
            "gpu_memory_used_bytes",
            "Used GPU memory in bytes",
            ["gpu_id", "name"],
        )
        self.gpu_memory_free = Gauge(
            "gpu_memory_free_bytes",
            "Free GPU memory in bytes",
            ["gpu_id", "name"],
        )
        self.gpu_utilization = Gauge(
            "gpu_utilization_percent",
            "GPU utilization percentage",
            ["gpu_id", "name"],
        )
        self.gpu_memory_utilization = Gauge(
            "gpu_memory_utilization_percent",
            "GPU memory utilization percentage",
            ["gpu_id", "name"],
        )
        self.gpu_fan_speed = Gauge(
            "gpu_fan_speed_percent",
            "GPU fan speed percentage",
            ["gpu_id", "name"],
        )

    async def collect_metrics(self) -> SystemMetrics:
        """Collect all metrics in our data model format.

        This method coordinates the collection of metrics from all collectors
        and validates them through our Pydantic models.

        Returns:
            SystemMetrics: Combined system metrics in our data model format.
        """
        # Collect raw metrics
        cpu_data = await self.cpu_collector.collect()
        memory_data = await self.memory_collector.collect()
        gpu_data = self.gpu_collector.collect_metrics()  # Note: This is not async

        # Validate through models
        return SystemMetrics(
            cpu=CPUMetrics(**cpu_data),
            memory=MemoryMetrics(**memory_data),
            gpu=GPUMetrics(**gpu_data),
        )

    def update_prometheus_metrics(self, metrics: SystemMetrics) -> None:
        """Update Prometheus metrics from our data model.

        This method takes our validated metrics model and updates all
        registered Prometheus gauges.

        Args:
            metrics: Validated system metrics.
        """
        # Update CPU metrics
        self.cpu_physical_count.set(metrics.cpu.count["physical"])
        self.cpu_logical_count.set(metrics.cpu.count["logical"])

        # Update frequencies if available
        if metrics.cpu.frequency["current"] is not None:
            self.cpu_frequency_current.set(metrics.cpu.frequency["current"])
        if metrics.cpu.frequency["min"] is not None:
            self.cpu_frequency_min.set(metrics.cpu.frequency["min"])
        if metrics.cpu.frequency["max"] is not None:
            self.cpu_frequency_max.set(metrics.cpu.frequency["max"])

        # Update CPU usage
        self.cpu_percent_total.set(metrics.cpu.percent["total"])
        for i, percent in enumerate(metrics.cpu.percent["per_cpu"]):
            self.cpu_percent_per_cpu.labels(core=str(i)).set(percent)

        # Update CPU stats
        self.cpu_ctx_switches.set(metrics.cpu.stats["ctx_switches"])
        self.cpu_interrupts.set(metrics.cpu.stats["interrupts"])
        self.cpu_soft_interrupts.set(metrics.cpu.stats["soft_interrupts"])
        self.cpu_syscalls.set(metrics.cpu.stats["syscalls"])

        # Update memory metrics
        self.memory_virtual_total.set(metrics.memory.virtual["total"])
        self.memory_virtual_available.set(metrics.memory.virtual["available"])
        self.memory_virtual_used.set(metrics.memory.virtual["used"])
        self.memory_virtual_free.set(metrics.memory.virtual["free"])
        self.memory_virtual_percent.set(metrics.memory.virtual["percent"])

        # Update swap metrics
        self.memory_swap_total.set(metrics.memory.swap["total"])
        self.memory_swap_used.set(metrics.memory.swap["used"])
        self.memory_swap_free.set(metrics.memory.swap["free"])
        self.memory_swap_percent.set(metrics.memory.swap["percent"])
        self.memory_swap_sin.set(metrics.memory.swap["sin"])
        self.memory_swap_sout.set(metrics.memory.swap["sout"])

        # Update GPU metrics
        self.gpu_device_count.set(metrics.gpu.device_count)

        for i, device in enumerate(metrics.gpu.devices):
            labels = {"gpu_id": str(i), "name": device.name}
            self.gpu_temperature.labels(**labels).set(device.temperature)
            self.gpu_power.labels(**labels).set(device.power_usage)
            self.gpu_memory_total.labels(**labels).set(device.memory_total)
            self.gpu_memory_used.labels(**labels).set(device.memory_used)
            self.gpu_memory_free.labels(**labels).set(device.memory_free)
            self.gpu_utilization.labels(**labels).set(device.utilization)
            self.gpu_memory_utilization.labels(**labels).set(device.memory_utilization)
            self.gpu_fan_speed.labels(**labels).set(device.fan_speed)

    def get_prometheus_metrics(self) -> bytes:
        """Get metrics in Prometheus format.

        Returns:
            bytes: Prometheus formatted metrics.
        """
        return generate_latest()
