from typing import Any

from taskiq.kicker import AsyncKicker, _FuncParams, _ReturnType
from taskiq.message import TaskiqMessage


class LabelRespectKicker(AsyncKicker[_FuncParams, _ReturnType]):
    """Patched kicker doesn't cast labels to str."""

    def _prepare_message(self, *args: Any, **kwargs: Any) -> TaskiqMessage:
        msg = super()._prepare_message(*args, **kwargs)
        msg.labels = self.labels
        return msg
