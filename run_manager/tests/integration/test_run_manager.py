import copy
from uuid import uuid4

import pytest

from common.entities import (
    AlertLevel,
    EventEntity,
    Instance,
    InstanceAlert,
    InstanceAlertType,
    InstanceSet,
    Pipeline,
    Run,
    RunAlert,
    RunAlertType,
    RunStatus,
    RunTask,
)
from common.entities.instance import InstanceStatus
from common.events.v1 import ApiRunStatus
from common.kafka import TOPIC_DEAD_LETTER_OFFICE, TOPIC_IDENTIFIED_EVENTS
from run_manager.context import RunManagerContext
from run_manager.event_handlers.run_unexpected_status_change_handler import _get_alert_type
from run_manager.run_manager import RunManager
from run_manager.tests.integration.conftest import compare_event_data
from testlib.fixtures.v1_events import valid_event_keys


@pytest.mark.integration
def test_create_alert_context_check(pipeline):
    ctx = RunManagerContext(pipeline=pipeline)
    with pytest.raises(ValueError):
        _get_alert_type(ctx)


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
def test_run_manager_no_project_id(event_key, kafka_consumer, kafka_producer, test_outcomes_message):
    test_outcomes_message.payload.event_id = uuid4()
    test_outcomes_message.payload.project_id = None
    test_outcomes_message.payload.pipeline_key = None
    setattr(test_outcomes_message.payload, event_key, "some-key")
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    kafka_producer.produce.assert_called_once_with(TOPIC_DEAD_LETTER_OFFICE, test_outcomes_message.payload)
    assert Pipeline.select().count() == 0
    assert Run.select().count() == 0


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
def test_run_manager_project_does_not_exist(event_key, kafka_consumer, kafka_producer, test_outcomes_message):
    test_outcomes_message.payload.event_id = uuid4()
    test_outcomes_message.payload.project_id = str(uuid4())
    test_outcomes_message.payload.pipeline_key = None
    setattr(test_outcomes_message.payload, event_key, "some-key")
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    kafka_producer.produce.assert_called_once_with(TOPIC_DEAD_LETTER_OFFICE, test_outcomes_message.payload)
    assert Pipeline.select().count() == 0
    assert Run.select().count() == 0


@pytest.mark.integration
def test_run_manager_close_nonexistent_pipeline(kafka_consumer, kafka_producer, completed_run_message, project):
    completed_run_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    kafka_producer.produce.assert_called_once()
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1


@pytest.mark.integration
def test_run_manager_close_nonexistent_run(kafka_consumer, kafka_producer, completed_run_message, project, pipeline):
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_key = pipeline.key
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    kafka_producer.produce.assert_called_once()
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1


@pytest.mark.integration
def test_run_manager_create_pipeline_run(kafka_consumer, kafka_producer, test_outcomes_message, project):
    test_outcomes_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == 1
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    pipeline = Pipeline.select().get()

    run = Run.select().get()

    # Run status should default to being created as "RUNNING"
    assert run.status == "RUNNING"

    kafka_producer.produce.assert_called_once()
    producer_args = kafka_producer.produce.call_args_list[0]
    actual_event = producer_args[0][1]

    assert producer_args[0][0] == TOPIC_IDENTIFIED_EVENTS
    compare_event_data(test_outcomes_message, actual_event, pipeline, run)


@pytest.mark.integration
@pytest.mark.parametrize(
    "status, run_task_started",
    (
        (ApiRunStatus.RUNNING, True),
        (ApiRunStatus.COMPLETED, False),
        (ApiRunStatus.COMPLETED_WITH_WARNINGS, False),
        (ApiRunStatus.FAILED, False),
    ),
)
def test_run_manager_status(
    kafka_consumer,
    kafka_producer,
    task_status_message,
    project,
    status,
    run_task_started,
):
    task_status_message.payload.event_id = uuid4()
    task_status_message.payload.status = status.name
    kafka_consumer.__iter__.return_value = iter((task_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == 1
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    pipeline = Pipeline.select().get()
    run = Run.select().get()
    assert len(pipeline.pipeline_tasks) == 1
    assert len(run.run_tasks) == 1
    task = pipeline.pipeline_tasks[0]
    run_task = run.run_tasks[0]
    assert task.key == task_status_message.payload.task_key
    assert run_task.status == task_status_message.payload.status
    assert run_task.start_time is not None
    if run_task_started:
        assert run_task.end_time is None
    else:
        assert run_task.end_time is not None

    kafka_producer.produce.assert_called_once()
    producer_args = kafka_producer.produce.call_args_list[0]
    actual_event = producer_args[0][1]

    assert producer_args[0][0] == TOPIC_IDENTIFIED_EVENTS
    compare_event_data(task_status_message, actual_event, pipeline, run)


@pytest.mark.integration
def test_run_manager_alert_warning(kafka_consumer, kafka_producer, run_status_message):
    assert RunAlert.select().count() == 0
    status_started = run_status_message
    status_started.payload.event_id = uuid4()
    status_warning = copy.deepcopy(run_status_message)
    status_warning.payload.event_id = uuid4()
    status_warning.payload.event_id = uuid4()
    status_warning.payload.status = ApiRunStatus.COMPLETED_WITH_WARNINGS.name
    kafka_consumer.__iter__.return_value = iter(
        (
            status_started,
            status_warning,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert EventEntity.select().count() == 2
    alert = RunAlert.select().get()
    assert alert.level == AlertLevel.WARNING
    assert alert.type == RunAlertType.COMPLETED_WITH_WARNINGS


@pytest.mark.integration
def test_run_manager_alert_error(kafka_consumer, kafka_producer, run_status_message):
    assert RunAlert.select().count() == 0
    status_started = run_status_message
    status_started.payload.event_id = uuid4()
    status_error = copy.deepcopy(run_status_message)
    status_error.payload.event_id = uuid4()
    status_error.payload.event_id = uuid4()
    status_error.payload.status = ApiRunStatus.FAILED.name
    kafka_consumer.__iter__.return_value = iter(
        (
            status_started,
            status_error,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert EventEntity.select().count() == 2
    alert = RunAlert.select().get()
    assert alert.level == AlertLevel.ERROR
    assert alert.type == RunAlertType.FAILED
    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
def test_run_manager_alert_inconsistent(kafka_consumer, kafka_producer, run_status_message, pipeline, journey):
    assert RunAlert.select().count() == 0
    status_started = run_status_message
    status_started.payload.event_id = uuid4()
    status_warning = copy.deepcopy(run_status_message)
    status_warning.payload.event_id = uuid4()
    status_warning.payload.event_id = uuid4()
    status_warning.payload.status = ApiRunStatus.COMPLETED_WITH_WARNINGS.name
    status_error = copy.deepcopy(run_status_message)
    status_error.payload.event_id = uuid4()
    status_error.payload.event_id = uuid4()
    status_error.payload.status = ApiRunStatus.FAILED.name
    kafka_consumer.__iter__.return_value = iter(
        (
            status_started,
            status_warning,
            status_error,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert EventEntity.select().count() == 3
    assert RunAlert.select().count() == 2
    alert = RunAlert.select().where(RunAlert.type == RunAlertType.UNEXPECTED_STATUS_CHANGE).get()
    assert alert.level == AlertLevel.WARNING
    alert_event = kafka_producer.produce.call_args_list[2][0][1]
    assert alert_event.level == AlertLevel.WARNING
    assert alert_event.type == RunAlertType.COMPLETED_WITH_WARNINGS
    alert_event = kafka_producer.produce.call_args_list[4][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
def test_run_manager_task_alert_warning(kafka_consumer, kafka_producer, task_status_message):
    assert RunAlert.select().count() == 0
    assert Run.select().count() == 0
    status_warning = copy.deepcopy(task_status_message)
    status_warning.payload.event_id = uuid4()
    status_warning.payload.event_id = uuid4()
    status_warning.payload.status = ApiRunStatus.COMPLETED_WITH_WARNINGS.name
    kafka_consumer.__iter__.return_value = iter((status_warning,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert EventEntity.select().count() == 1
    assert Run.select().count() == 1
    assert Run.get().status == RunStatus.RUNNING.name
    assert RunTask.select().count() == 1
    assert RunTask.get().status == RunStatus.COMPLETED_WITH_WARNINGS.name
    assert RunAlert.select().count() == 0


@pytest.mark.integration
def test_run_manager_multiple_status(kafka_consumer, kafka_producer, task_status_message, project):
    def copy_with_status(status):
        event_msg = copy.deepcopy(task_status_message)
        event_msg.payload.event_id = uuid4()
        event_msg.payload.status = status.name
        return event_msg

    messages = [
        copy_with_status(status)
        for status in (
            ApiRunStatus.COMPLETED,
            ApiRunStatus.COMPLETED_WITH_WARNINGS,
            ApiRunStatus.FAILED,
            ApiRunStatus.COMPLETED,
            ApiRunStatus.COMPLETED_WITH_WARNINGS,
            ApiRunStatus.FAILED,
        )
    ]

    kafka_consumer.__iter__.return_value = iter(messages)
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == len(messages)
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    pipeline = Pipeline.select().get()
    run = Run.select().get()
    assert len(pipeline.pipeline_tasks) == 1
    assert len(run.run_tasks) == 1
    task = pipeline.pipeline_tasks[0]
    run_task = run.run_tasks[0]

    assert kafka_producer.produce.call_count == 6

    for event_msg, producer_args in zip(messages, kafka_producer.produce.call_args_list, strict=True):
        actual_event = producer_args[0][1]
        compare_event_data(event_msg, actual_event, pipeline, run, task, run_task)


@pytest.mark.integration
def test_run_manager_close_single_run(kafka_consumer, kafka_producer, test_outcomes_message, completed_run_message):
    test_outcomes_message.payload.event_id = uuid4()
    completed_run_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter(
        (
            test_outcomes_message,
            completed_run_message,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == 2
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    pipeline = Pipeline.select().get()
    run = Run.select().get()

    assert run.end_time is not None
    assert kafka_producer.produce.call_count == 2
    producer_args1 = kafka_producer.produce.call_args_list[0]
    producer_args2 = kafka_producer.produce.call_args_list[1]
    assert producer_args1[0][0] == TOPIC_IDENTIFIED_EVENTS
    assert producer_args2[0][0] == TOPIC_IDENTIFIED_EVENTS
    actual_event1 = producer_args1[0][1]
    actual_event2 = producer_args2[0][1]

    compare_event_data(test_outcomes_message, actual_event1, pipeline, run)
    compare_event_data(test_outcomes_message, actual_event2, pipeline, run)


@pytest.mark.integration
def test_run_manager_with_tag_close_run_and_create_new(
    kafka_consumer, kafka_producer, test_outcomes_message, completed_run_message
):
    test_outcomes_message.payload.event_id = uuid4()
    test_outcomes_message2 = copy.deepcopy(test_outcomes_message)
    completed_run_message.payload.event_id = uuid4()
    test_outcomes_message2.payload.event_id = uuid4()
    test_outcomes_message2.payload.run_key += "2"
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message, completed_run_message, test_outcomes_message2))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == 3
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 2
    run1, run2 = list(Run.select())
    assert run1.end_time is not None
    assert run2.end_time is None
    assert kafka_producer.produce.call_count == 3


@pytest.mark.integration
def test_run_manager_set_run_name(kafka_consumer, kafka_producer, test_outcomes_message, running_run_message):
    run_manager = RunManager(kafka_consumer, kafka_producer)

    # Set name with run status
    the_name = str(uuid4())
    running_run_message.payload.event_id = uuid4()
    running_run_message.payload.run_name = the_name
    kafka_consumer.__iter__.return_value = iter((running_run_message,))
    run_manager.process_events()
    assert Run.select().get().name == the_name

    # Update name with update with run status
    the_name = str(uuid4())
    running_run_message.payload.event_id = uuid4()
    running_run_message.payload.run_name = the_name
    kafka_consumer.__iter__.return_value = iter((running_run_message,))
    run_manager.process_events()
    assert Run.select().get().name == the_name

    # Update name with update with test outcomes
    the_name = str(uuid4())
    test_outcomes_message.payload.event_id = uuid4()
    test_outcomes_message.payload.run_name = the_name
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager.process_events()
    assert Run.select().get().name == the_name


@pytest.mark.integration
def test_run_manager_generate_out_of_sequence_alert_on_new_run(
    simple_dag, kafka_consumer, kafka_producer, task_status_message, running_run_message, pipeline, pipeline2
):
    assert Run.select().count() == 0

    running_run_message.payload.event_id = uuid4()
    task_status_message.payload.event_id = uuid4()
    task_status_message.payload.pipeline_key = pipeline2.key

    kafka_consumer.__iter__.return_value = iter(
        (
            running_run_message,
            task_status_message,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == 2
    assert Pipeline.select().count() == 2
    assert Run.select().count() == 2
    run1 = Run.select().where(Run.pipeline == pipeline.id).get()
    run2 = Run.select().where(Run.pipeline == pipeline2.id).get()
    assert run1.status == RunStatus.RUNNING.name
    assert run2.status == RunStatus.RUNNING.name
    assert InstanceAlert.select().where(InstanceAlert.type == InstanceAlertType.OUT_OF_SEQUENCE.name).count() == 1
    assert Instance.select().count() == 1
    assert Instance.get().status == InstanceStatus.ERROR.value


@pytest.mark.integration
def test_run_manager_generate_out_of_sequence_alert_on_existing_run(
    simple_dag, kafka_consumer, kafka_producer, instance, task_status_message, pipeline, pipeline2
):
    for p in [pipeline, pipeline2]:
        Run.create(
            status=RunStatus.RUNNING.name, key=p.key, pipeline=p, instance_set=InstanceSet.get_or_create([instance.id])
        )
    assert Run.select().count() == 2

    task_status_message.payload.event_id = uuid4()
    task_status_message.payload.pipeline_key = pipeline2.key
    task_status_message.payload.run_key = pipeline2.key
    kafka_consumer.__iter__.return_value = iter((task_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == 1
    assert Pipeline.select().count() == 2
    assert Run.select().count() == 2
    assert InstanceAlert.select().where(InstanceAlert.type == InstanceAlertType.OUT_OF_SEQUENCE.name).count() == 0


@pytest.mark.integration
def test_run_manager_out_of_sequence_alert_different_event_types(
    mixed_dag,
    kafka_consumer,
    kafka_producer,
    completed_run_message,
    test_outcomes_message,
    message_log_message,
    metric_log_message,
    running_run_message,
    pipeline,
    server,
    stream,
    dataset,
):
    assert Run.select().count() == 0

    test_outcomes_message.payload.event_id = uuid4()
    test_outcomes_message.payload.dataset_key = dataset.key
    message_log_message.payload.event_id = uuid4()
    message_log_message.payload.server_key = server.key
    metric_log_message.payload.event_id = uuid4()
    metric_log_message.payload.stream = stream.key
    completed_run_message.payload.event_id = uuid4()

    kafka_consumer.__iter__.return_value = iter(
        (
            test_outcomes_message,
            message_log_message,
            metric_log_message,
            completed_run_message,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert EventEntity.select().count() == 4
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert InstanceAlert.select().where(InstanceAlert.type == InstanceAlertType.OUT_OF_SEQUENCE.name).count() == 0
