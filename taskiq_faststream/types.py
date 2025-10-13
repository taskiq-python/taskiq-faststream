from datetime import datetime, timedelta

from typing_extensions import TypedDict


class ScheduledTask(TypedDict, total=False):
    """Store information about scheduled tasks.

    https://taskiq-python.github.io/available-components/schedule-sources.html
    """

    cron: str
    cron_offset: str | timedelta | None
    time: datetime | None
