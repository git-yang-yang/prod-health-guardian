"""Metrics collector coordination module."""

from typing import Any

from prometheus_client.core import GaugeMetricFamily

from ..collectors.cpu import CPUCollector
from ..collectors.memory import MemoryCollector


class MetricsCollector:
    """Collector for exposing metrics in Prometheus format.
    
    This class coordinates multiple collectors and converts their metrics
    into Prometheus format. It follows the Prometheus collector interface
    for custom collectors.
    """

    def __init__(self) -> None:
        """Initialize metrics collector with hardware collectors."""
        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()

    def collect(self) -> list[GaugeMetricFamily]:
        """Collect all metrics and convert to Prometheus format.

        This method implements the Prometheus collector interface.
        It gathers metrics from all collectors and converts them to
        Prometheus gauge metrics.

        Returns:
            list[GaugeMetricFamily]: List of Prometheus metrics
        """
        metrics = []
        
        # Collect CPU metrics
        cpu_metrics = self.cpu_collector.collect_metrics()
        metrics.extend(self._create_cpu_metrics(cpu_metrics))
        
        # Collect memory metrics
        memory_metrics = self.memory_collector.collect_metrics()
        metrics.extend(self._create_memory_metrics(memory_metrics))
        
        return metrics

    def _create_cpu_metrics(
        self,
        cpu_metrics: dict[str, Any]
    ) -> list[GaugeMetricFamily]:
        """Create Prometheus metrics for CPU data.
        
        Args:
            cpu_metrics: Dictionary containing CPU metrics
            
        Returns:
            list[GaugeMetricFamily]: List of Prometheus CPU metrics
        """
        metrics = []

        # CPU Counts
        cpu_counts = GaugeMetricFamily(
            'cpu_count',
            'Number of CPU cores',
            labels=['type']
        )
        cpu_counts.add_metric(['physical'], cpu_metrics['count']['physical'])
        cpu_counts.add_metric(['logical'], cpu_metrics['count']['logical'])
        metrics.append(cpu_counts)

        # CPU Frequencies
        for freq_type in ['current', 'min', 'max']:
            if cpu_metrics['frequency'][freq_type] is not None:
                freq = GaugeMetricFamily(
                    f'cpu_frequency_{freq_type}_mhz',
                    f'{freq_type.title()} CPU frequency in MHz'
                )
                freq.add_metric([], cpu_metrics['frequency'][freq_type])
                metrics.append(freq)

        # CPU Usage
        cpu_usage = GaugeMetricFamily(
            'cpu_percent',
            'CPU usage percentage',
            labels=['core']
        )
        cpu_usage.add_metric(['total'], cpu_metrics['percent']['total'])
        for i, percent in enumerate(cpu_metrics['percent']['per_cpu']):
            cpu_usage.add_metric([str(i)], percent)
        metrics.append(cpu_usage)

        # CPU Stats
        for stat_name, value in cpu_metrics['stats'].items():
            stat = GaugeMetricFamily(
                f'cpu_{stat_name}_total',
                f'Total number of {stat_name.replace("_", " ")}'
            )
            stat.add_metric([], value)
            metrics.append(stat)

        return metrics

    def _create_memory_metrics(
        self,
        memory_metrics: dict[str, Any]
    ) -> list[GaugeMetricFamily]:
        """Create Prometheus metrics for memory data.
        
        Args:
            memory_metrics: Dictionary containing memory metrics
            
        Returns:
            list[GaugeMetricFamily]: List of Prometheus memory metrics
        """
        metrics = []

        # Virtual Memory
        for key, value in memory_metrics['virtual'].items():
            if key == 'percent':
                name = 'memory_virtual_percent'
                desc = 'Virtual memory usage percentage'
            else:
                name = f'memory_virtual_{key}_bytes'
                desc = f'{key.title()} virtual memory in bytes'
            
            metric = GaugeMetricFamily(name, desc)
            metric.add_metric([], value)
            metrics.append(metric)

        # Swap Memory
        for key, value in memory_metrics['swap'].items():
            if key == 'percent':
                name = 'memory_swap_percent'
                desc = 'Swap memory usage percentage'
            elif key in ['sin', 'sout']:
                name = f'memory_swap_{key}_total'
                desc = f'Total memory pages swapped {key[1:]}'
            else:
                name = f'memory_swap_{key}_bytes'
                desc = f'{key.title()} swap memory in bytes'
            
            metric = GaugeMetricFamily(name, desc)
            metric.add_metric([], value)
            metrics.append(metric)

        return metrics 