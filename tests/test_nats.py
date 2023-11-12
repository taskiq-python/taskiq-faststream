import asyncio
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from anyio import Event
from faststream.nats import NatsBroker, TestNatsBroker
from faststream.utils.functions import timeout_scope
from taskiq import TaskiqScheduler
from taskiq.cli.scheduler.args import SchedulerArgs
from taskiq.cli.scheduler.run import run_scheduler
from taskiq.schedule_sources import LabelScheduleSource

from taskiq_faststream import BrokerWrapper


@pytest.fixture
def broker() -> NatsBroker:
    return NatsBroker()


@pytest.mark.anyio
async def test_time_task(
    subject: str,
    broker: NatsBroker,
    mock: MagicMock,
    event: Event,
) -> None:
    @broker.subscriber(subject)
    async def handler(msg: str) -> None:
        event.set()
        mock(msg)

    taskiq_broker = BrokerWrapper(broker)

    taskiq_broker.task(
        "Hi!",
        subject=subject,
        schedule=[
            {
                "time": datetime.utcnow(),
            },
        ],
    )

    async with TestNatsBroker(broker):
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
