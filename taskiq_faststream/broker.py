import typing
import warnings
from typing import Any, TypeAlias

import anyio
from faststream._internal.application import Application
from faststream.types import SendableMessage
from taskiq import AsyncBroker
from taskiq.acks import AckableMessage
from taskiq.decor import AsyncTaskiqDecoratedTask

from taskiq_faststream.formatter import PatchedFormatter, PatchedMessage
from taskiq_faststream.types import ScheduledTask
from taskiq_faststream.utils import resolve_msg

try:
    from taskiq.middlewares.otel_middleware import OpenTelemetryMiddleware
except ImportError:
    OpenTelemetryMiddleware = None  # type: ignore[assignment,misc]

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

    def __init__(
        self,
        broker: Any,
        *,
        enable_otel: bool = False,
    ) -> None:
        """Initialize BrokerWrapper.

        Args:
            broker: FastStream broker instance to wrap.
            enable_otel: Enable OpenTelemetry middleware for distributed tracing.
                Requires taskiq[otel] to be installed.
        """
        super().__init__()
        self.formatter = PatchedFormatter()
        self.broker = broker

        if enable_otel:
            if OpenTelemetryMiddleware is None:
                msg = (
                    "OpenTelemetry middleware requires taskiq[otel] to be installed. "
                    "Install it with: pip install taskiq-faststream[otel]"
                )
                raise ImportError(msg)
            self.middlewares.append(OpenTelemetryMiddleware())

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
    ) -> typing.AsyncGenerator[bytes | AckableMessage, None]:
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
        message: None
        | SendableMessage
        | typing.Callable[[], SendableMessage]
        | typing.Callable[[], typing.Awaitable[SendableMessage]]
        | typing.Callable[[], typing.Generator[SendableMessage, None, None]]
        | typing.Callable[[], typing.AsyncGenerator[SendableMessage, None]] = None,
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

    def __init__(
        self,
        app: Application,
        *,
        enable_otel: bool = False,
    ) -> None:
        """Initialize AppWrapper.

        Args:
            app: FastStream application instance to wrap.
            enable_otel: Enable OpenTelemetry middleware for distributed tracing.
                Requires taskiq[otel] to be installed.
        """
        super(BrokerWrapper, self).__init__()
        self.formatter = PatchedFormatter()
        self.app = app

        if enable_otel:
            if OpenTelemetryMiddleware is None:
                msg = (
                    "OpenTelemetry middleware requires taskiq[otel] to be installed. "
                    "Install it with: pip install taskiq-faststream[otel]"
                )
                raise ImportError(msg)
            self.middlewares.append(OpenTelemetryMiddleware())

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
