import copy
from datetime import datetime, timedelta, timezone, UTC
from uuid import uuid4

import pytest

from common.entities import InstanceAlert, InstanceAlertType, Run, RunTask
from common.events.v1 import ApiRunStatus
from run_manager.run_manager import RunManager


@pytest.mark.integration
def test_keep_run_end_state_and_update_start_state(pipeline, kafka_consumer, kafka_producer, run_status_message):
    """
    Keep the run end state (end time, status) when an old message is processed.
    Update the start time when older message is received.
    """
    new_time = datetime.now(tz=UTC)
    old_time = new_time - timedelta(minutes=5)

    old_start_status_message = run_status_message
    old_start_status_message.payload.event_timestamp = old_time
    old_start_status_message.payload.status = ApiRunStatus.RUNNING.name

    new_status_message = copy.deepcopy(run_status_message)
    new_status_message.payload.event_id = uuid4()
    new_status_message.payload.event_timestamp = new_time
    new_status_message.payload.status = ApiRunStatus.COMPLETED.name

    old_end_status_message = copy.deepcopy(run_status_message)
    old_end_status_message.payload.event_id = uuid4()
    old_end_status_message.payload.event_timestamp = old_time
    old_end_status_message.payload.status = ApiRunStatus.FAILED.name

    kafka_consumer.__iter__.return_value = iter((new_status_message, old_start_status_message, old_end_status_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    run = Run.get()
    assert run.status == ApiRunStatus.COMPLETED.name
    assert run.start_time == old_time
    assert run.end_time == new_time


@pytest.mark.integration
def test_reopen_run_on_newer_status(
    pipeline, kafka_consumer, kafka_producer, completed_run_message, run_status_message
):
    completed_run_message.payload.event_id = uuid4()
    run_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message, completed_run_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Run.select().count() == 1
    run = Run.get()
    assert run.status == ApiRunStatus.COMPLETED.name
    assert run.end_time is not None

    # Re-open existing run
    run_status_message.payload.event_timestamp = datetime.utcnow().replace(tzinfo=UTC)
    run_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager.process_events()

    assert Run.select().count() == 1
    run = Run.get()
    assert run.status == ApiRunStatus.RUNNING.name
    assert run.end_time is None


@pytest.mark.integration
def test_keep_task_end_state_and_update_start_state(kafka_consumer, kafka_producer, task_status_message):
    """
    Keep the task end state (end time, status) when an old message is processed.
    Update the start time when older message is received.
    """
    new_time = datetime.now(tz=UTC)
    old_time = new_time - timedelta(minutes=5)
    old_status_message = task_status_message
    old_status_message.payload.event_timestamp = old_time
    old_status_message.payload.status = ApiRunStatus.RUNNING.name
    new_status_message = copy.deepcopy(task_status_message)
    new_status_message.payload.event_id = uuid4()
    new_status_message.payload.event_timestamp = new_time
    new_status_message.payload.status = ApiRunStatus.COMPLETED.name

    kafka_consumer.__iter__.return_value = iter((new_status_message, old_status_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    run = Run.get()
    assert run.status == ApiRunStatus.RUNNING.name
    assert run.start_time == new_time

    assert RunTask.select().count() == 1
    run_task = RunTask.get()
    assert run_task.status == ApiRunStatus.COMPLETED.name
    assert run_task.start_time == old_time
    assert run_task.end_time == new_time


@pytest.mark.integration
def test_reopen_task_on_newer_status(pipeline, kafka_consumer, kafka_producer, run_status_message):
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.task_key = "task-key-1"
    completed_task_message = copy.deepcopy(run_status_message)
    completed_task_message.payload.event_id = uuid4()
    completed_task_message.payload.status = ApiRunStatus.FAILED.name

    kafka_consumer.__iter__.return_value = iter((run_status_message, completed_task_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert RunTask.select().count() == 1
    run = RunTask.get()
    assert run.status == ApiRunStatus.FAILED.name
    assert run.end_time is not None

    # Re-open existing run
    run_status_message.payload.event_timestamp = datetime.utcnow().replace(tzinfo=UTC)
    run_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager.process_events()

    assert RunTask.select().count() == 1
    run = RunTask.get()
    assert run.status == ApiRunStatus.RUNNING.name
    assert run.end_time is None


@pytest.mark.integration
def test_out_of_sequence_runs_with_out_of_sequence_events(
    pipeline, pipeline2, simple_dag, kafka_consumer, kafka_producer, run_status_message
):
    complete_run = copy.deepcopy(run_status_message)
    complete_run.payload.event_id = uuid4()
    complete_run.payload.status = ApiRunStatus.COMPLETED.name
    complete_run.payload.event_timestamp = run_status_message.payload.event_timestamp + timedelta(minutes=60)
    start_second_run = copy.deepcopy(run_status_message)
    start_second_run.payload.event_id = uuid4()
    start_second_run.payload.pipeline_key = pipeline2.key
    start_second_run.payload.event_timestamp = run_status_message.payload.event_timestamp + timedelta(minutes=30)
    kafka_consumer.__iter__.return_value = iter((run_status_message, complete_run, start_second_run))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert pipeline.pipeline_runs.count() == 1
    assert pipeline2.pipeline_runs.count() == 1
    run1 = pipeline.pipeline_runs[0]
    run2 = pipeline2.pipeline_runs[0]
    assert run1.start_time < run1.end_time
    assert run1.start_time < run2.start_time
    assert run1.end_time > run2.start_time

    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.get()
    assert alert.type == InstanceAlertType.OUT_OF_SEQUENCE
