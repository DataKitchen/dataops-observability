import copy
from datetime import timedelta
from uuid import uuid4

import pytest

from common.entities import Pipeline, Run, RunTask, RunTaskStatus, Task
from common.events.v1 import ApiRunStatus
from common.events.v1.event import EVENT_ATTRIBUTES
from run_manager.run_manager import RunManager
from run_manager.tests.integration.conftest import compare_event_data
from testlib.fixtures.v1_events import valid_event_keys


@pytest.mark.integration
def test_run_manager_multiple_tasks_in_run(pipeline, kafka_consumer, kafka_producer, run_status_message):
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.task_key = "task-key-1"
    run_status_message2 = copy.deepcopy(run_status_message)
    run_status_message2.payload.event_id = uuid4()
    run_status_message2.payload.task_key = "task-key-2"
    kafka_consumer.__iter__.return_value = iter((run_status_message, run_status_message2))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert kafka_producer.produce.call_count == 2
    pipeline = Pipeline.select().get()
    run = Run.select().get()
    assert len(pipeline.pipeline_tasks) == 2
    assert len(run.run_tasks) == 2
    for input_name in (run_status_message.payload.task_key, run_status_message2.payload.task_key):
        task = Task.select().where(Task.key == input_name).get()
        assert len(task.run_tasks) == 1


@pytest.mark.integration
def test_run_manager_same_task_in_different_runs(
    kafka_consumer, kafka_producer, task_status_message, completed_run_message
):
    task_status_message.payload.event_id = uuid4()
    completed_run_message.payload.event_id = uuid4()
    run_status_message2 = copy.deepcopy(task_status_message)
    run_status_message2.payload.event_id = uuid4()
    run_status_message2.payload.run_key = uuid4()
    kafka_consumer.__iter__.return_value = iter((task_status_message, completed_run_message, run_status_message2))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 2
    assert Task.select().count() == 1
    assert RunTask.select().count() == 2
    assert kafka_producer.produce.call_count == 3
    pipeline = Pipeline.select().get()
    assert len(pipeline.pipeline_tasks) == 1
    task = pipeline.pipeline_tasks[0]
    for run in Run.select():
        assert len(run.run_tasks) == 1
        run_task = run.run_tasks[0]
        assert run_task.task_id == task.id


@pytest.mark.integration
def test_run_manager_close_closed_run(
    pipeline, kafka_consumer, kafka_producer, run_status_message, completed_run_message
):
    completed_run_message.payload.event_id = uuid4()
    completed_run_message2 = copy.deepcopy(completed_run_message)

    run_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # At this point there should be 1 open run
    assert Run.select().where(Run.end_time == None).count() == 1

    completed_run_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # And now 0 open runs
    assert Run.select().where(Run.end_time is None).count() == 0
    assert Run.select().count() == 1  # (but still 1 actual run)

    # Re-closing the same run
    completed_run_message2.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((completed_run_message2,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().where(Run.end_time is None).count() == 0
    assert Run.select().count() == 1


@pytest.mark.integration
def test_run_manager_status_starting_after_close_run(
    pipeline, kafka_consumer, kafka_producer, task_status_message, completed_run_message
):
    task_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((task_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert kafka_producer.produce.call_count == 1
    pipeline = Pipeline.select().get()
    run = Run.select().get()
    assert len(pipeline.pipeline_tasks) == 1
    assert len(run.run_tasks) == 1
    run_task = run.run_tasks[0]
    assert run_task.status == task_status_message.payload.status
    assert run_task.start_time is not None
    assert run_task.end_time is None

    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager.process_events()

    # Closing the run does not affect the started run tasks
    assert run_task.status == task_status_message.payload.status
    assert run_task.end_time is None


@pytest.mark.integration
def test_run_manager_do_not_create_nonrequired_run_tasks(
    kafka_consumer, kafka_producer, task_status_message, completed_run_message, message_log_message
):
    task_status_message.payload.event_id = uuid4()
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.run_key = uuid4()
    message_log_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((task_status_message, completed_run_message, message_log_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 2
    assert Task.select().count() == 1
    assert RunTask.select().count() == 1
    assert Run.select().where(Run.status == RunTaskStatus.RUNNING.name).count() == 1


@pytest.mark.integration
def test_run_manager_precreate_required_runtasks(
    kafka_consumer, kafka_producer, run_status_message, task_status_message, message_log_message, completed_run_message
):
    task_status_message.payload.event_id = uuid4()
    completed_run_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((task_status_message, completed_run_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    # Step 1: Create run and task
    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 1
    assert RunTask.select().count() == 1
    assert kafka_producer.produce.call_count == 2
    run = Run.select().get()
    assert run.end_time
    run_task = RunTask.select().get()
    assert not run_task.required
    assert run_task.start_time is not None

    task = Task.select().get()
    task.required = True
    task.save()

    # Step 2: Auto create required RunTask
    message_log_message.payload.event_id = uuid4()
    message_log_message.payload.run_key = uuid4()
    kafka_consumer.__iter__.return_value = iter((message_log_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Pipeline.select().count() == 1
    # assert Run.select().count() == 2
    assert Task.select().count() == 1
    assert RunTask.select().count() == 2
    run = Run.select().where(Run.status == RunTaskStatus.RUNNING.name).get()
    assert len(run.run_tasks) == 1
    run_task = run.run_tasks[0]
    assert run_task.status == RunTaskStatus.PENDING.name
    assert run_task.required
    assert run_task.start_time is None

    # Step 3: Close run with pending required tasks
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.run_key = message_log_message.payload.run_key
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    run_task = RunTask.get_by_id(run_task.id)
    assert run_task.status == RunTaskStatus.MISSING.name

    # Step 4: Reopen run with missing required tasks
    completed_run_message.payload.run_key = message_log_message.payload.run_key
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.run_key = message_log_message.payload.run_key
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    run_task = RunTask.get_by_id(run_task.id)
    assert run_task.status == RunTaskStatus.PENDING.name


@pytest.mark.integration
def test_run_manager_set_newest_task_status(project, kafka_consumer, kafka_producer, run_status_message):
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_id = None
    run_status_message.payload.task_key = "task-1"
    run_status_message.payload.status = ApiRunStatus.COMPLETED_WITH_WARNINGS.name
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()
    assert RunTask.select().count() == 1
    run_task1 = RunTask.select().get()
    assert run_task1.status == ApiRunStatus.COMPLETED_WITH_WARNINGS.name
    assert run_task1.end_time is not None

    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.status = ApiRunStatus.COMPLETED.name
    run_status_message.payload.event_timestamp += timedelta(hours=1)
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 1
    assert RunTask.select().count() == 1
    run_task2 = RunTask.select().get()
    assert run_task2.start_time is not None
    assert run_task2.end_time is not None
    # New end time should be set
    assert run_task2.end_time != run_task1.end_time
    # Deescalated task status
    assert run_task2.status == ApiRunStatus.COMPLETED.name


@pytest.mark.parametrize(
    "event_fixture",
    (
        ("metric_log_message"),
        ("message_log_message"),
        ("test_outcomes_message"),
    ),
)
@pytest.mark.integration
def test_run_manager_first_task_key_is_starting_task(pipeline, kafka_consumer, kafka_producer, event_fixture, request):
    event = request.getfixturevalue(event_fixture)
    event.payload.event_id = uuid4()
    event.payload.task_key = "a task key"
    kafka_consumer.__iter__.return_value = iter((event,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 1
    assert RunTask.select().count() == 1
    assert kafka_producer.produce.call_count == 1
    producer_args = kafka_producer.produce.call_args_list[0]

    actual_event = producer_args[0][1]
    pipeline = Pipeline.select().get()
    run = Run.select().get()
    task = Task.select().get()
    run_task = RunTask.select().get()

    assert run_task.status == RunTaskStatus.RUNNING.name
    assert run_task.start_time is not None
    assert run_task.end_time is None
    compare_event_data(event, actual_event, pipeline, run, task, run_task)


@pytest.mark.integration
@pytest.mark.parametrize("event_key", [key for key in valid_event_keys if key != "pipeline_key"])
@pytest.mark.parametrize("event_fixture", ["metric_log_message", "message_log_message", "test_outcomes_message"])
def test_task_handler_non_batch_pipeline_event_do_not_create_new_task(
    event_key, event_fixture, request, kafka_consumer, kafka_producer
):
    event_msg = request.getfixturevalue(event_fixture)
    event_msg.payload.event_id = uuid4()
    event_msg.payload.pipeline_key = None
    event_msg.payload.run_key = None
    event_msg.payload.task_key = "a task key"
    setattr(event_msg.payload, EVENT_ATTRIBUTES.get(event_key).component_key, "some key")

    kafka_consumer.__iter__.return_value = iter((event_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EVENT_ATTRIBUTES.get(event_key).component_model.select().count() == 1
    assert Pipeline.select().count() == 0
    assert Run.select().count() == 0
    assert Task.select().count() == 0
    assert RunTask.select().count() == 0
    assert kafka_producer.produce.call_count == 1
