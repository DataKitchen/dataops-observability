__all__ = ["UpcomingInstance"]
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from common.entities.journey import Journey


@dataclass
class UpcomingInstance:
    journey: Journey
    expected_start_time: Optional[datetime] = None
    expected_end_time: Optional[datetime] = None
