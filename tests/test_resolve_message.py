from collections.abc import AsyncIterator, Iterator

import pytest

from taskiq_faststream.utils import resolve_msg


@pytest.mark.anyio
async def test_regular() -> None:
    async for m in resolve_msg("msg"):
        assert m == "msg"


@pytest.mark.anyio
async def test_sync_callable() -> None:
    async for m in resolve_msg(lambda: "msg"):
        assert m == "msg"


@pytest.mark.anyio
async def test_async_callable() -> None:
    async def gen_msg() -> str:
        return "msg"

    async for m in resolve_msg(gen_msg):
        assert m == "msg"


@pytest.mark.anyio
async def test_sync_callable_class() -> None:
    class C:
        def __init__(self) -> None:
            pass

        def __call__(self) -> str:
            return "msg"

    async for m in resolve_msg(C()):
        assert m == "msg"


@pytest.mark.anyio
async def test_async_callable_class() -> None:
    class C:
        def __init__(self) -> None:
            pass

        async def __call__(self) -> str:
            return "msg"

    async for m in resolve_msg(C()):
        assert m == "msg"


@pytest.mark.anyio
async def test_async_generator() -> None:
    async def get_msg() -> AsyncIterator[str]:
        yield "msg"

    async for m in resolve_msg(get_msg):
        assert m == "msg"


@pytest.mark.anyio
async def test_sync_generator() -> None:
    def get_msg() -> Iterator[str]:
        yield "msg"

    async for m in resolve_msg(get_msg):
        assert m == "msg"
