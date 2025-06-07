from dataclasses import dataclass
from typing import Any

from taskiq.abc.formatter import TaskiqFormatter
from taskiq.message import TaskiqMessage


@dataclass
class PatchedMessage:
    """DTO to transfer data to `broker.kick`."""

    body: Any
    labels: dict[str, Any]


class PatchedFormatter(TaskiqFormatter):
    """Default taskiq formatter."""

    def dumps(  # type: ignore[override]
        self,
        message: TaskiqMessage,
    ) -> PatchedMessage:
        """
        Dumps taskiq message to some broker message format.

        :param message: message to send.
        :return: Dumped message.
        """
        labels = message.labels.copy()
        labels.pop("schedule", None)
        labels.pop("schedule_id", None)

        return PatchedMessage(
            body=labels.pop("message", None),
            labels=labels,
        )

    def loads(self, message: bytes) -> TaskiqMessage:
        """
        Loads json from message.

        :param message: broker's message.
        :return: parsed taskiq message.
        """
        raise NotImplementedError
