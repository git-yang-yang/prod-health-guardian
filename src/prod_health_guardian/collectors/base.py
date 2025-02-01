"""Base collector module."""

from abc import ABC, abstractmethod
from typing import Any


class BaseCollector(ABC):
    """Base class for all metric collectors.

    This abstract base class defines the interface that all metric collectors
    must implement. It ensures a consistent pattern for collecting metrics
    across different hardware components.
    """

    @abstractmethod
    async def collect(self) -> dict[str, Any]:
        """Collect metrics from the hardware component.

        This method must be implemented by all collectors to gather metrics
        from their respective hardware components.

        Returns:
            dict[str, Any]: Collected metrics in a dictionary format.
        """
        raise NotImplementedError

    @property
    def is_available(self) -> bool:
        """Check if the collector can collect metrics on this system.

        Returns:
            bool: True if collector can collect metrics, False otherwise.
        """
        return True
