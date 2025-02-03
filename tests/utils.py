"""Test utilities and helper functions."""

from typing import Any


class AsyncMock:
    """Helper class to create async mock objects."""

    def __init__(self, return_value: Any) -> None:
        """Initialize with return value.

        Args:
            return_value: Value to return when called.
        """
        self.return_value = return_value

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Async call that returns the stored value.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: The stored return value.
        """
        return self.return_value
