import pytest

from taskiq_faststream import BrokerWrapper


@pytest.mark.anyio
async def test_warning() -> None:
    broker = BrokerWrapper(None)

    with pytest.warns(RuntimeWarning):
        async for _ in broker.listen():  # pragma: no branch
            break
