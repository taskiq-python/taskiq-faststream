import typing
import warnings
from typing import Any

import anyio
from faststream._internal.application import Application
from faststream.types import SendableMessage
from taskiq import AsyncBroker
from taskiq.acks import AckableMessage
from taskiq.decor import AsyncTaskiqDecoratedTask
from typing_extensions import TypeAlias

from taskiq_faststream.formatter import PatchedFormatter, PatchedMessage
from taskiq_faststream.types import ScheduledTask
from taskiq_faststream.utils import resolve_msg

PublishParameters: TypeAlias = typing.Any


class BrokerWrapper(AsyncBroker):
    """Wrap FastStream broker to taskiq compatible object.

    Attributes:
        broker : FastStream wrapped broker.

    Methods:
        __init__ : Initializes the object.
        startup : Startup wrapped FastStream broker.
        shutdown : Shutdown wrapped FastStream broker.
        kick : Call wrapped FastStream broker `publish` method.
        task : Register FastStream scheduled task.
    """

    def __init__(self, broker: Any) -> None:
        super().__init__()
        self.formatter = PatchedFormatter()
        self.broker = broker

    async def startup(self) -> None:
        """Startup wrapped FastStream broker."""
        await super().startup()
        await self.broker.start()

    async def shutdown(self) -> None:
        """Shutdown wrapped FastStream broker."""
        await self.broker.close()
        await super().shutdown()

    async def kick(self, message: PatchedMessage) -> None:  # type: ignore[override]
        """Call wrapped FastStream broker `publish` method."""
        await _broker_publish(self.broker, message)

    async def listen(
        self,
    ) -> typing.AsyncGenerator[typing.Union[bytes, AckableMessage], None]:
        """Not supported method."""
        while True:
            warnings.warn(
                message=(
                    f"{self.__class__.__name__} doesn't support `listen` method. "
                    "Please, use it only to register a task."
                ),
                category=RuntimeWarning,
                stacklevel=1,
            )
            yield b""
            await anyio.sleep(60)

    def task(  # type: ignore[override]
        self,
        message: typing.Union[
            None,
            SendableMessage,
            typing.Callable[[], SendableMessage],
            typing.Callable[[], typing.Awaitable[SendableMessage]],
            typing.Callable[[], typing.Generator[SendableMessage, None, None]],
            typing.Callable[[], typing.AsyncGenerator[SendableMessage, None]],
        ] = None,
        *,
        schedule: list[ScheduledTask],
        **kwargs: PublishParameters,
    ) -> "AsyncTaskiqDecoratedTask[[], None]":
        """Register FastStream scheduled task.

        Args:
            message: object to send or sync/async message generation callback.
            schedule: scheduler parameters list.
            kwargs: `broker.publish(...)` arguments.
        """
        return super().task(
            message=message,
            schedule=schedule,
            **kwargs,
        )(lambda: None)


class AppWrapper(BrokerWrapper):
    """Wrap FastStream instance to taskiq compatible object.

    Attributes:
        app : FastStream instance.

    Methods:
        __init__ : Initializes the object.
        startup : Startup wrapped FastStream.
        shutdown : Shutdown wrapped FastStream.
        kick : Call wrapped FastStream broker `publish` method.
        task : Register FastStream scheduled task.
    """

    def __init__(self, app: Application) -> None:
        super(BrokerWrapper, self).__init__()
        self.formatter = PatchedFormatter()
        self.app = app

    async def startup(self) -> None:
        """Startup wrapped FastStream."""
        await super(BrokerWrapper, self).startup()
        await self.app._startup()  # noqa: SLF001

    async def shutdown(self) -> None:
        """Shutdown wrapped FastStream."""
        await self.app._shutdown()  # noqa: SLF001
        await super(BrokerWrapper, self).shutdown()

    async def kick(self, message: PatchedMessage) -> None:  # type: ignore[override]
        """Call wrapped FastStream broker `publish` method."""
        assert (  # noqa: S101
            self.app.broker
        ), "You should setup application broker firts"
        await _broker_publish(self.app.broker, message)


async def _broker_publish(
    broker: Any,
    message: PatchedMessage,
) -> None:
    async for msg in resolve_msg(message.body):
        await broker.publish(msg, **message.labels)
