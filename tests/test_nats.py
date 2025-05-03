import pytest
from faststream import FastStream
from faststream.nats import NatsBroker, TestNatsBroker
from taskiq import AsyncBroker

from taskiq_faststream import AppWrapper

from .testcase import SchedulerTestcase


@pytest.fixture
def broker() -> NatsBroker:
    return NatsBroker()


class TestBroker(SchedulerTestcase):
    test_class = TestNatsBroker
    subj_name = "subject"


class TestApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: NatsBroker) -> AsyncBroker:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker))


class TestAsgiApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: NatsBroker) -> AsyncBroker:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker).as_asgi())
