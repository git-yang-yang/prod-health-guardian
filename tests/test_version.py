"""Basic tests to verify test infrastructure."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

MOCK_RETURN_VALUE = 42


def test_basic_setup() -> None:
    """Basic test to verify pytest setup is working.

    This test will always pass and is used to confirm the test infrastructure
    is properly configured.
    """
    assert True


def test_mock_example(mocker: "MockerFixture") -> None:
    """Example test demonstrating mock usage.

    Args:
        mocker: Pytest fixture for mocking.
    """
    mock = mocker.Mock(return_value=MOCK_RETURN_VALUE)
    assert mock() == MOCK_RETURN_VALUE
