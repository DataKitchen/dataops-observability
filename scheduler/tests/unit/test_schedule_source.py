from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from apscheduler.triggers.cron import CronTrigger

from scheduler.schedule_source import RunTimeExecutor, ScheduleSource


class TestScheduleSource(ScheduleSource):
    source_name = "test"

    def _create_and_add_job(self, schedule):
        yield Mock()

    def _get_schedules(self):
        yield Mock()

    def update(self) -> None:
        pass


@pytest.fixture
def scheduler():
    yield Mock()


@pytest.fixture
def event_producer_mock():
    return Mock()


@pytest.fixture
def schedule_source(scheduler, event_producer_mock):
    yield TestScheduleSource(scheduler, event_producer_mock)


@pytest.fixture
def submit_job_mock():
    yield Mock()


@pytest.fixture
def run_time_executor(submit_job_mock):
    with patch("scheduler.schedule_source.ThreadPoolExecutor.submit_job", submit_job_mock):
        yield RunTimeExecutor()


@pytest.mark.unit
def test_schedule_source_add_job(schedule_source, scheduler):
    func = Mock()
    trigger = CronTrigger.from_crontab("* * * * *")
    kwargs = {"arg1": "value1"}
    schedule_source.add_job(func=func, job_id="some ID", trigger=trigger, kwargs=kwargs)

    scheduler.add_job.assert_called_with(
        func, id="some ID", trigger=trigger, kwargs=kwargs, jobstore="test", executor="test"
    )


@pytest.mark.unit
def test_runtime_executor_adds_runtime(run_time_executor, submit_job_mock):
    job = Mock()
    job.kwargs = {"run_time": None}
    run_time = datetime.utcnow()

    run_time_executor.submit_job(job, [run_time])

    job.modify.assert_called_once_with(kwargs={"run_time": run_time})
    submit_job_mock.assert_called_once_with(job, [run_time])


@pytest.mark.unit
def test_runtime_executor_does_not_touch_job(run_time_executor, submit_job_mock):
    job = Mock()
    job.kwargs = {"some_random_arg": 42}
    run_time = datetime.utcnow()

    run_time_executor.submit_job(job, [run_time])

    job.modify.assert_not_called()
    submit_job_mock.assert_called_once_with(job, [run_time])
