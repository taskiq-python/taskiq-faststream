import asyncio
import typing
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import MagicMock

import pytest
from faststream.types import SendableMessage
from faststream.utils.functions import timeout_scope
from freezegun import freeze_time
from taskiq import AsyncBroker
from taskiq.cli.scheduler.args import SchedulerArgs
from taskiq.cli.scheduler.run import run_scheduler
from taskiq.schedule_sources import LabelScheduleSource

from taskiq_faststream import BrokerWrapper, StreamScheduler
from tests import messages


@pytest.mark.anyio
class SchedulerTestcase:
    test_class: Any
    subj_name: str

    @staticmethod
    def build_taskiq_broker(broker: Any) -> AsyncBroker:
        """Build Taskiq compatible object."""
        return BrokerWrapper(broker)

    async def test_task(
        self,
        subject: str,
        broker: Any,
        mock: MagicMock,
        event: asyncio.Event,
    ) -> None:
        """Base testcase."""

        @broker.subscriber(subject)
        async def handler(msg: str) -> None:
            event.set()
            mock(msg)

        taskiq_broker = self.build_taskiq_broker(broker)

        taskiq_broker.task(
            "Hi!",
            **{self.subj_name: subject},
            schedule=[
                {
                    "time": datetime.now(tz=timezone.utc),
                },
            ],
        )

        async with self.test_class(broker):
            task = asyncio.create_task(
                run_scheduler(
                    SchedulerArgs(
                        scheduler=StreamScheduler(
                            broker=taskiq_broker,
                            sources=[LabelScheduleSource(taskiq_broker)],
                        ),
                        modules=[],
                    ),
                ),
            )

            with timeout_scope(3.0, True):
                await event.wait()

        mock.assert_called_once_with("Hi!")
        task.cancel()

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
    async def test_task_multiple_schedules_by_cron(
        self,
        subject: str,
        broker: Any,
        event: asyncio.Event,
        msg: typing.Union[
            None,
            SendableMessage,
            typing.Callable[[], SendableMessage],
            typing.Callable[[], typing.Awaitable[SendableMessage]],
            typing.Callable[[], typing.Generator[SendableMessage, None, None]],
            typing.Callable[[], typing.AsyncGenerator[SendableMessage, None]],
        ],
    ) -> None:
        """Test cron runs twice via StreamScheduler."""
        received_message = []

        @broker.subscriber(subject)
        async def handler(message: str) -> None:
            received_message.append(message)
            event.set()

        taskiq_broker = self.build_taskiq_broker(broker)

        taskiq_broker.task(
            msg,
            **{self.subj_name: subject},
            schedule=[
                {
                    "cron": "* * * * *",
                },
            ],
        )

        async with self.test_class(broker):
            with freeze_time("00:00:00", tick=True) as frozen_datetime:
                task = asyncio.create_task(
                    run_scheduler(
                        SchedulerArgs(
                            scheduler=StreamScheduler(
                                broker=taskiq_broker,
                                sources=[LabelScheduleSource(taskiq_broker)],
                            ),
                            modules=[],
                        ),
                    ),
                )

                await asyncio.wait_for(event.wait(), 2.0)
                event.clear()
                frozen_datetime.tick(timedelta(minutes=2))
                await asyncio.wait_for(event.wait(), 2.0)

            task.cancel()

        assert received_message == [messages.message, messages.message], (
            received_message
        )
