from typing import TYPE_CHECKING

from taskiq.scheduler.scheduled_task import ScheduledTask
from taskiq.scheduler.scheduler import TaskiqScheduler as Scheduler
from taskiq.utils import maybe_awaitable

from taskiq_faststream.kicker import LabelRespectKicker

if TYPE_CHECKING:  # pragma: no cover
    from taskiq.abc.schedule_source import ScheduleSource


class StreamScheduler(Scheduler):
    """Patched scheduler with custom kicker."""

    async def on_ready(self, source: "ScheduleSource", task: ScheduledTask) -> None:
        """
        This method is called when task is ready to be enqueued.

        It's triggered on proper time depending on `task.cron` or `task.time` attribute.
        :param task: task to send
        """
        await maybe_awaitable(source.pre_send(task))
        await LabelRespectKicker(task.task_name, self.broker, task.labels).kiq(
            *task.args,
            **task.kwargs,
        )
        await maybe_awaitable(source.post_send(task))
