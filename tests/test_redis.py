import pytest
from faststream import FastStream
from faststream.redis import RedisBroker, TestRedisBroker

from taskiq_faststream import AppWrapper

from .testcase import SchedulerTestcase


@pytest.fixture
def broker() -> RedisBroker:
    return RedisBroker()


class TestBroker(SchedulerTestcase):
    test_class = TestRedisBroker
    subj_name = "channel"


class TestApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: RedisBroker) -> AppWrapper:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker))


class TestAsgiApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: RedisBroker) -> AppWrapper:
        """Build AppWrapper."""
        return AppWrapper(FastStream(broker).as_asgi())
