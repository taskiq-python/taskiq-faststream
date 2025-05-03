import asyncio
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import pytest
from faststream.utils.functions import timeout_scope
from taskiq import AsyncBroker, TaskiqScheduler
from taskiq.cli.scheduler.args import SchedulerArgs
from taskiq.cli.scheduler.run import run_scheduler
from taskiq.schedule_sources import LabelScheduleSource

from taskiq_faststream import BrokerWrapper


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
                        scheduler=TaskiqScheduler(
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
