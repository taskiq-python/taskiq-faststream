import pytest
from faststream import FastStream
from faststream.rabbit import RabbitBroker, TestRabbitBroker
from taskiq import AsyncBroker

from taskiq_faststream import AppWrapper

from .testcase import SchedulerTestcase


@pytest.fixture
def broker() -> RabbitBroker:
    return RabbitBroker()


class TestBroker(SchedulerTestcase):
    test_class = TestRabbitBroker
    subj_name = "queue"


class TestApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: RabbitBroker) -> AsyncBroker:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker))


class TestAsgiApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: RabbitBroker) -> AsyncBroker:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker).as_asgi())
