"""Base class for metric collectors."""

from abc import ABC, abstractmethod
from typing import Any


class MetricCollector(ABC):
    """Base class for all metric collectors."""

    @abstractmethod
    def get_name(self) -> str:
        """Get collector name.

        Returns:
            str: Name of the collector.
        """
        pass

    @abstractmethod
    async def collect(self) -> dict[str, Any]:
        """Collect metrics.

        Returns:
            dict[str, Any]: Collected metrics data.
        """
        pass

    @property
    def is_available(self) -> bool:
        """Check if the collector can collect metrics on this system.

        Returns:
            bool: True if collector can collect metrics, False otherwise.
        """
        return True 