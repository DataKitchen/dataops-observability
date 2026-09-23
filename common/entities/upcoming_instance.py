__all__ = ["UpcomingInstance"]
from dataclasses import dataclass
from datetime import datetime

from common.entities.journey import Journey


@dataclass
class UpcomingInstance:
    journey: Journey
    expected_start_time: datetime | None = None
    expected_end_time: datetime | None = None
