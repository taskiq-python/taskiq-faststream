import pytest
from faststream import FastStream
from faststream.kafka import KafkaBroker, TestKafkaBroker
from taskiq import AsyncBroker

from taskiq_faststream import AppWrapper

from .testcase import SchedulerTestcase


@pytest.fixture
def broker() -> KafkaBroker:
    return KafkaBroker()


class TestBroker(SchedulerTestcase):
    test_class = TestKafkaBroker
    subj_name = "topic"


class TestApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: KafkaBroker) -> AsyncBroker:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker))


class TestAsgiApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: KafkaBroker) -> AsyncBroker:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker).as_asgi())
