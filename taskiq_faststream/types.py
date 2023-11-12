from datetime import datetime, timedelta
from typing import Optional, Union

from faststream._compat import TypedDict


class ScheduledTask(TypedDict, total=False):
    """Store information about scheduled tasks.

    https://taskiq-python.github.io/available-components/schedule-sources.html
    """

    cron: str
    cron_offset: Union[str, timedelta, None]
    time: Optional[datetime]
