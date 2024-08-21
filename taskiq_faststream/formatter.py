from typing import Any, Dict

from taskiq.abc.broker import AsyncBroker
from taskiq.abc.formatter import TaskiqFormatter
from taskiq.compat import IS_PYDANTIC2, Model, model_dump, model_validate
from taskiq.message import BrokerMessage, TaskiqMessage

if IS_PYDANTIC2:

    def model_dump(instance: Model) -> Dict[str, Any]:
        """Model dump."""
        return instance.model_dump()

else:

    def model_dump(instance: Model) -> Dict[str, Any]:
        """Model dump."""
        return instance.dict()


class PatchedFormatter(TaskiqFormatter):
    """Default taskiq formatter."""

    def __init__(self, broker: AsyncBroker) -> None:
        self.broker = broker

    def dumps(self, message: TaskiqMessage) -> BrokerMessage:
        """
        Dumps taskiq message to some broker message format.

        :param message: message to send.
        :return: Dumped message.
        """
        return BrokerMessage(
            task_id=message.task_id,
            task_name=message.task_name,
            message=self.broker.serializer.dumpb(model_dump(message)),
            labels=message.labels,
        )

    def loads(self, message: bytes) -> TaskiqMessage:
        """
        Loads json from message.

        :param message: broker's message.
        :return: parsed taskiq message.
        """
        return model_validate(TaskiqMessage, self.broker.serializer.loadb(message))
