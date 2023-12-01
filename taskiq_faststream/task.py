from taskiq.decor import AsyncTaskiqDecoratedTask as Task
from taskiq.decor import _FuncParams, _ReturnType

from taskiq_faststream.kicker import LabelRespectKicker


class PatchedTaskiqDecoratedTask(Task[_FuncParams, _ReturnType]):
    """Patched Decorated Task has a patched kicker."""

    def kicker(self) -> LabelRespectKicker[_FuncParams, _ReturnType]:
        """
        This function returns kicker object.

        Kicker is a object that can modify kiq request
        before sending it.

        :return: AsyncKicker instance.
        """
        return LabelRespectKicker(
            task_name=self.task_name,
            broker=self.broker,
            labels=self.labels,
        )
