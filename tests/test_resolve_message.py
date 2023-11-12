import pytest

from taskiq_faststream.utils import resolve_msg


@pytest.mark.anyio
async def test_regular() -> None:
    assert await resolve_msg("msg") == "msg"


@pytest.mark.anyio
async def test_sync_callable() -> None:
    assert await resolve_msg(lambda: "msg") == "msg"


@pytest.mark.anyio
async def test_async_callable() -> None:
    async def gen_msg() -> str:
        return "msg"

    assert await resolve_msg(gen_msg) == "msg"


@pytest.mark.anyio
async def test_sync_callable_class() -> None:
    class C:
        def __init__(self) -> None:
            pass

        def __call__(self) -> str:
            return "msg"

    assert await resolve_msg(C()) == "msg"


@pytest.mark.anyio
async def test_async_callable_class() -> None:
    class C:
        def __init__(self) -> None:
            pass

        async def __call__(self) -> str:
            return "msg"

    assert await resolve_msg(C()) == "msg"
