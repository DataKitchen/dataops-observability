__all__ = [
    "MISSING_run_status_event",
    "batch_start_margin_schedule_event",
    "PENDING_run_status_event",
]

from datetime import datetime
from uuid import uuid4

import pytest

from common.entities import RunStatus
from common.events.enums import EventSources, ScheduleType
from common.events.internal import ScheduledEvent
from common.events.v1 import RunStatusEvent
from testlib.fixtures.v1_events import pipeline_id


@pytest.fixture
def batch_start_margin_schedule_event():
    return ScheduledEvent(
        schedule_id=uuid4(),
        component_id=uuid4(),
        schedule_timestamp=datetime.now(),
        schedule_margin=None,
        schedule_type=ScheduleType.BATCH_START_TIME_MARGIN,
    )


@pytest.fixture
def PENDING_run_status_event(batch_start_margin_schedule_event, event_data):
    data = event_data.copy()
    data.update(
        {
            "event_type": RunStatusEvent.__name__,
            "status": RunStatus.PENDING.name,
            "pipeline_id": pipeline_id,
            "run_key": None,
            "run_id": None,
            "source": EventSources.SCHEDULER.name,
            "event_timestamp": batch_start_margin_schedule_event.schedule_margin,
            "received_timestamp": batch_start_margin_schedule_event.schedule_margin,
        }
    )
    return RunStatusEvent(**data)


@pytest.fixture
def MISSING_run_status_event(timestamp_now, event_data, pipeline, pending_run):
    data = event_data.copy()
    data.update(
        {
            "event_type": RunStatusEvent.__name__,
            "status": RunStatus.MISSING.name,
            "pipeline_id": pipeline_id,
            "run_id": pending_run.id,
            "run_key": None,
            "source": EventSources.SCHEDULER.name,
            "event_timestamp": timestamp_now,
            "received_timestamp": timestamp_now,
        }
    )
    return RunStatusEvent(**data)
