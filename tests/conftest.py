from asyncio import Event
from unittest.mock import MagicMock
from uuid import uuid4

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Anyio backend.

    Backend for anyio pytest plugin.
    :return: backend name.
    """
    return "asyncio"


@pytest.fixture()
def subject() -> str:
    return uuid4().hex


@pytest.fixture()
def mock() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def event() -> Event:
    return Event()
