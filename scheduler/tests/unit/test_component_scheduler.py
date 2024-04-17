from datetime import datetime
from unittest.mock import patch

import pytest

from common.entities import Schedule, ScheduleExpectation
from common.events.enums import ScheduleType
from common.events.internal import ScheduledEvent
from common.kafka import TOPIC_SCHEDULED_EVENTS


@pytest.mark.unit
@pytest.mark.parametrize("schedule_type", [e for e in ScheduleType])
def test_component_source_produce_event(schedule_type, component_source, event_producer_mock, job_kwargs):
    if schedule_type != ScheduleType.BATCH_END_TIME:
        job_kwargs["margin"] = 10
        job_kwargs["is_margin"] = True
    job_kwargs["schedule_type"] = schedule_type.name

    component_source._produce_event(**job_kwargs)

    (topic, event), _ = event_producer_mock.produce.call_args_list[0]
    assert topic == TOPIC_SCHEDULED_EVENTS
    assert isinstance(event, ScheduledEvent)
    assert event.schedule_id == job_kwargs["schedule_id"]
    assert event.schedule_type == job_kwargs["schedule_type"]
    assert event.component_id == job_kwargs["component_id"]
    assert type(event.schedule_timestamp) is datetime
    if schedule_type != ScheduleType.BATCH_END_TIME:
        assert type(event.schedule_margin) is datetime


@pytest.mark.unit
def test_component_source_add_job_start_time(schedule_data, component_source, scheduler):
    sched = Schedule(**schedule_data)

    with patch.object(component_source, "add_job") as add_job_mock:
        component_source._create_and_add_job(sched)

    for idx, s_type in ((0, ScheduleType.BATCH_START_TIME), (1, ScheduleType.BATCH_START_TIME_MARGIN)):
        job_kwargs = add_job_mock.call_args_list[idx][1]
        assert job_kwargs.keys() == {"job_id", "trigger", "kwargs"}
        assert job_kwargs["job_id"].endswith(s_type.value), job_kwargs
        assert job_kwargs["kwargs"]["schedule_type"] == s_type, job_kwargs
        assert job_kwargs["kwargs"]["schedule_id"] == schedule_data["id"], job_kwargs
        assert job_kwargs["kwargs"]["component_id"] == schedule_data["component"], job_kwargs
        assert job_kwargs["kwargs"]["margin"] == schedule_data["margin"], job_kwargs
        assert job_kwargs["kwargs"]["is_margin"] == (s_type == ScheduleType.BATCH_START_TIME_MARGIN)


@pytest.mark.unit
def test_component_source_add_job_end_time(schedule_data, component_source, scheduler):
    schedule_data["expectation"] = ScheduleExpectation.BATCH_PIPELINE_END_TIME.value
    schedule_data["margin"] = None
    sched = Schedule(**schedule_data)

    with patch.object(component_source, "add_job") as add_job_mock:
        component_source._create_and_add_job(sched)

    job_kwargs = add_job_mock.call_args_list[0][1]
    assert job_kwargs.keys() == {"job_id", "trigger", "kwargs"}
    assert job_kwargs["job_id"].endswith(ScheduleType.BATCH_END_TIME.value), job_kwargs
    assert job_kwargs["kwargs"]["schedule_type"] == ScheduleType.BATCH_END_TIME, job_kwargs
    assert job_kwargs["kwargs"]["schedule_id"] == schedule_data["id"], job_kwargs
    assert job_kwargs["kwargs"]["component_id"] == schedule_data["component"], job_kwargs
    assert job_kwargs["kwargs"]["margin"] == schedule_data["margin"], job_kwargs
    assert job_kwargs["kwargs"]["is_margin"] is False


@pytest.mark.unit
def test_component_source_add_job_dataset(schedule_data, component_source, scheduler):
    schedule_data["expectation"] = ScheduleExpectation.DATASET_ARRIVAL.value
    schedule_data["margin"] = 60
    sched = Schedule(**schedule_data)

    with patch.object(scheduler, "add_job") as add_job_mock:
        component_source._create_and_add_job(sched)

    job_kwargs = add_job_mock.call_args_list[0][1]
    assert len(job_kwargs.keys() & {"id", "kwargs", "jobstore"}) == 3, job_kwargs
    assert job_kwargs["id"].endswith(ScheduleType.DATASET_ARRIVAL_MARGIN.value), job_kwargs
    assert job_kwargs["jobstore"] == "component_expectations", job_kwargs
    assert job_kwargs["kwargs"]["schedule_type"] == ScheduleType.DATASET_ARRIVAL_MARGIN, job_kwargs
    assert job_kwargs["kwargs"]["schedule_id"] == schedule_data["id"], job_kwargs
    assert job_kwargs["kwargs"]["component_id"] == schedule_data["component"], job_kwargs
    assert job_kwargs["kwargs"]["margin"] == schedule_data["margin"], job_kwargs
    assert job_kwargs["kwargs"]["is_margin"] is True
