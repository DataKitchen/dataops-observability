from datetime import datetime
from uuid import uuid4

import pytest

from common.events.enums import ScheduleType
from common.events.internal import ScheduledEvent
from run_manager.event_handlers import handle_schedule_event


@pytest.mark.unit
@pytest.mark.parametrize("schedule_type", (ScheduleType.BATCH_START_TIME_MARGIN, ScheduleType.DATASET_ARRIVAL_MARGIN))
def test_schedule_event_missing_margin_timestamp(schedule_type):
    event = ScheduledEvent(
        schedule_id=uuid4(),
        component_id=uuid4(),
        schedule_timestamp=datetime.now(),
        schedule_margin=None,
        schedule_type=schedule_type,
    )
    with pytest.raises(ValueError):
        handle_schedule_event(event)
