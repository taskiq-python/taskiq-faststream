import typing
import warnings

from faststream._compat import TypeAlias, override
from faststream.broker.core.asyncronous import BrokerAsyncUsecase
from faststream.types import SendableMessage
from taskiq import AsyncBroker, BrokerMessage
from taskiq.acks import AckableMessage
from taskiq.decor import AsyncTaskiqDecoratedTask

from taskiq_faststream.types import ScheduledTask
from taskiq_faststream.utils import resolve_msg

PublishParameters: TypeAlias = typing.Any


class BrokerWrapper(AsyncBroker):
    """Wrap FastStream broker to taskiq compatible object.

    Attributes:
        broker : FastStream wrapped broker.

    Methods:
        __init__ : Initializes the object.
        startup : Startup wrapper FastStream broker.
        shutdown : Shutdown wrapper FastStream broker.
        kick : Call wrapped FastStream broker `publish` method.
        task : Register FastStream scheduled task.
    """

    def __init__(self, broker: BrokerAsyncUsecase[typing.Any, typing.Any]) -> None:
        super().__init__()
        self.broker = broker

    async def startup(self) -> None:
        """Startup wrapper FastStream broker."""
        await super().startup()
        await self.broker.start()

    async def shutdown(self) -> None:
        """Shutdown wrapper FastStream broker."""
        await self.broker.close()
        await super().shutdown()

    async def kick(self, message: BrokerMessage) -> None:
        """Call wrapped FastStream broker `publish` method."""
        labels = message.labels
        labels.pop("schedule", None)
        msg = await resolve_msg(labels.pop("message", message.message))
        await self.broker.publish(msg, **labels)

    async def listen(
        self,
    ) -> typing.AsyncGenerator[typing.Union[bytes, AckableMessage], None]:
        """Not supported method."""
        warnings.warn(
            message=(
                f"{self.__class__.__name__} doesn't support `listen` method. "
                "Please, use it only to register a task."
            ),
            category=RuntimeWarning,
            stacklevel=1,
        )

        while True:
            yield b""

    @override
    def task(  # type: ignore[override]
        self,
        message: typing.Union[
            None,
            SendableMessage,
            typing.Callable[[], SendableMessage],
            typing.Callable[[], typing.Awaitable[SendableMessage]],
        ] = None,
        *,
        schedule: typing.List[ScheduledTask],
        **kwargs: PublishParameters,
    ) -> AsyncTaskiqDecoratedTask[[], None]:
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
