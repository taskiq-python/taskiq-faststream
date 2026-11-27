import pytest
from faststream import FastStream
from faststream.mqtt import MQTTBroker, TestMQTTBroker

from taskiq_faststream import AppWrapper

from .testcase import SchedulerTestcase


@pytest.fixture
def broker() -> MQTTBroker:
    return MQTTBroker()


class TestBroker(SchedulerTestcase):
    test_class = TestMQTTBroker
    subj_name = "topic"


class TestApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: MQTTBroker) -> AppWrapper:
        """Wrap a FastStream app backed by MQTT."""
        return AppWrapper(FastStream(broker))


class TestAsgiApp(TestBroker):
    @staticmethod
    def build_taskiq_broker(broker: MQTTBroker) -> AppWrapper:
        """Wrap a FastStream ASGI app backed by MQTT."""
        return AppWrapper(FastStream(broker).as_asgi())
