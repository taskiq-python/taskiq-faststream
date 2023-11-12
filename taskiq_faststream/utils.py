import typing

from faststream.types import SendableMessage
from faststream.utils.functions import to_async


async def resolve_msg(
    msg: typing.Union[
        None,
        SendableMessage,
        typing.Callable[[], SendableMessage],
        typing.Callable[[], typing.Awaitable[SendableMessage]],
    ],
) -> SendableMessage:
    """Resolve message generation callback.

    Args:
        msg: object to send or sync/async message generation callback.

    Returns:
        The message to send
    """
    if callable(msg):
        get_msg = typing.cast(
            typing.Callable[[], typing.Awaitable[SendableMessage]],
            to_async(msg),
        )
        msg = await get_msg()
    return msg
