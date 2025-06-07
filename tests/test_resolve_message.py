import typing

import pytest
from faststream.types import SendableMessage

from taskiq_faststream.utils import resolve_msg
from tests import messages


@pytest.mark.parametrize(
    "msg",
    [
        messages.message,  # regular msg
        messages.sync_callable_msg,  # sync callable
        messages.async_callable_msg,  # async callable
        messages.sync_generator_msg,  # sync generator
        messages.async_generator_msg,  # async generator
        messages.sync_callable_class_message,  # sync callable class
        messages.async_callable_class_message,  # async callable class
    ],
)
@pytest.mark.anyio
async def test_resolve_msg(
    msg: typing.Union[
        None,
        SendableMessage,
        typing.Callable[[], SendableMessage],
        typing.Callable[[], typing.Awaitable[SendableMessage]],
        typing.Callable[[], typing.Generator[SendableMessage, None, None]],
        typing.Callable[[], typing.AsyncGenerator[SendableMessage, None]],
    ],
) -> None:
    async for m in resolve_msg(msg):
        assert m == messages.message
