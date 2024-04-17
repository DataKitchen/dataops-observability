import threading
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.base import BaseTrigger

from common.entities import InstanceRule, InstanceRuleAction, Schedule, ScheduleExpectation
from common.kafka.topic import Topic
from scheduler.component_expectations import ComponentScheduleSource
from scheduler.instance_expectations import InstanceScheduleSource
from scheduler.schedule_source import ScheduleSource
from testlib.fixtures.entities import *


class TestScheduler(BaseScheduler):
    def wakeup(self):
        return super().wakeup()

    def shutdown(self, wait=True):
        return super().shutdown(wait)


class TestTrigger(BaseTrigger):
    """Trigger that is always due, and only triggers once."""

    def get_next_fire_time(self, previous_fire_time, now):
        if previous_fire_time:
            return None
        else:
            return datetime.now(tz=timezone.utc)


class TestScheduleSource(ScheduleSource):
    source_name = "test"
    kafka_topic = Topic

    def _create_and_add_job(self, schedule: Schedule):
        yield Mock()

    def _get_schedules(self):
        yield Mock()


@pytest.fixture
def get_due_jobs_mock():
    yield Mock()


@pytest.fixture
def scheduler():
    s = TestScheduler()
    s.start()
    yield s
    s.shutdown()


@pytest.fixture
def event_producer_mock():
    return Mock()


@pytest.fixture
def schedule_source(get_due_jobs_mock, scheduler, event_producer_mock):
    with patch("scheduler.schedule_source.MemoryJobStore.get_due_jobs", get_due_jobs_mock):
        source = TestScheduleSource(scheduler, event_producer_mock)
        scheduler.remove_jobstore("default")
        yield source


@pytest.fixture
def component_source(get_due_jobs_mock, scheduler, event_producer_mock):
    with patch("scheduler.schedule_source.MemoryJobStore.get_due_jobs", get_due_jobs_mock):
        source = ComponentScheduleSource(scheduler, event_producer_mock)
        scheduler.remove_jobstore("default")
        yield source


@pytest.fixture
def instance_rule_source(get_due_jobs_mock, scheduler, event_producer_mock):
    with patch("scheduler.schedule_source.MemoryJobStore.get_due_jobs", get_due_jobs_mock):
        source = InstanceScheduleSource(scheduler, event_producer_mock)
        scheduler.remove_jobstore("default")
        yield source


def create_schedule(
    component,
    expectation=ScheduleExpectation.BATCH_PIPELINE_START_TIME.value,
    schedule="* * * * *",
    timezone="UTC",
    margin=60,
):
    return Schedule.create(
        component=component,
        expectation=expectation,
        schedule=schedule,
        timezone=timezone,
        margin=margin,
    )


@pytest.mark.integration
def test_component_source_update(scheduler, component_source, pipeline):
    assert len(scheduler.get_jobs(component_source.jobstore_name)) == 0

    # Adding newly created schedules. START_TIME creates 2 jobs
    s1 = create_schedule(pipeline)
    component_source.update()
    assert len(scheduler.get_jobs(component_source.jobstore_name)) == 2

    # Adding an END_TIME schedule
    create_schedule(pipeline, expectation=ScheduleExpectation.BATCH_PIPELINE_END_TIME.value)
    component_source.update()
    assert len(scheduler.get_jobs(component_source.jobstore_name)) == 3

    # Deleted schedule should be removed
    s1.delete_instance()
    component_source.update()
    assert len(scheduler.get_jobs(component_source.jobstore_name)) == 1


@pytest.mark.integration
def test_instance_source_empty_expression_no_update(scheduler, instance_rule_source, journey, pipeline):
    _ = InstanceRule.create(journey=journey, action=InstanceRuleAction.END, batch_pipeline_id=pipeline.id)
    assert len(scheduler.get_jobs(instance_rule_source.jobstore_name)) == 0
    assert InstanceRule.select().count() == 1
    instance_rule_source.update()
    assert len(scheduler.get_jobs(instance_rule_source.jobstore_name)) == 0


@pytest.mark.integration
def test_instance_source_update(scheduler, instance_rule_source, instance, instance_rule_start, instance_rule_end):
    assert len(scheduler.get_jobs(instance_rule_source.jobstore_name)) == 0
    assert InstanceRule.select().count() == 2

    instance_rule_source.update()
    assert len(scheduler.get_jobs(instance_rule_source.jobstore_name)) == 2

    InstanceRule.delete().where(InstanceRule.id == instance_rule_start.id).execute()
    assert InstanceRule.select().count() == 1

    instance_rule_source.update()
    assert len(scheduler.get_jobs(instance_rule_source.jobstore_name)) == 1


@pytest.mark.integration
def test_schedule_source_set_run_time_arg(get_due_jobs_mock, scheduler, schedule_source):
    """Tests that the `run_time` job arg is being injected properly on each run."""
    event = threading.Event()
    func = Mock()
    func.side_effect = lambda **_: event.set()

    job = schedule_source.add_job(
        func,
        job_id="test_job",
        trigger=TestTrigger(),
        kwargs={"run_time": None},
    )
    get_due_jobs_mock.return_value = [job]

    scheduler._process_jobs()
    assert event.wait(0.5), "mock wasn't called within 0.5 sec"
    assert type(func.call_args.kwargs["run_time"]) is datetime
