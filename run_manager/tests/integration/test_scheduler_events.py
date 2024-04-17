from collections import Counter
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from common.entities import (
    AlertLevel,
    DatasetOperation,
    DatasetOperationType,
    Instance,
    InstanceAlert,
    InstanceAlertType,
    InstanceSet,
    InstancesInstanceSets,
    Pipeline,
    Run,
    RunAlert,
    RunAlertType,
    RunStatus,
    Schedule,
    ScheduleExpectation,
)
from common.entities.instance import InstanceStatus
from common.events.enums import ScheduleType
from common.events.internal import InstanceAlert as InstanceAlertEvent
from common.events.internal import RunAlert as RunAlertEvent
from common.events.internal import ScheduledEvent
from common.kafka import TOPIC_SCHEDULED_EVENTS, KafkaMessage
from common.user_strings.alert_descriptions import RUN_ALERT_DESCRIPTIONS
from run_manager.run_manager import RunManager


@pytest.fixture
def schedule_pipeline(pipeline):
    return Schedule.create(
        component=pipeline,
        schedule="",
        timezone="UTC",
        expectation=ScheduleExpectation.BATCH_PIPELINE_START_TIME,
        margin="60",
    )


@pytest.fixture
def schedule_dataset(dataset):
    return Schedule.create(
        component=dataset,
        schedule="",
        timezone="UTC",
        expectation=ScheduleExpectation.DATASET_ARRIVAL,
        margin="60",
    )


@pytest.fixture
def scheduler_event_base(timestamp_now, schedule_pipeline):
    """Common scheduler event fields to be used to build and event"""
    return {
        "schedule_id": schedule_pipeline.id,
        "component_id": schedule_pipeline.component_id,
        "schedule_timestamp": timestamp_now,
    }


@pytest.fixture
def scheduler_kafka_message_base():
    return {
        "topic": TOPIC_SCHEDULED_EVENTS.name,
        "partition": 2,
        "offset": 1,
        "headers": {},
    }


@pytest.fixture
def batch_start_schedule(scheduler_kafka_message_base, scheduler_event_base):
    """Scheduler event with type BATCH_START_TIME"""
    return KafkaMessage(
        **scheduler_kafka_message_base,
        payload=ScheduledEvent(
            **scheduler_event_base,
            schedule_type=ScheduleType.BATCH_START_TIME,
        ),
    )


@pytest.fixture
def batch_start_margin_schedule(scheduler_kafka_message_base, scheduler_event_base, timestamp_future):
    """Scheduler event with type BATCH_START_TIME_MARGIN"""
    return KafkaMessage(
        **scheduler_kafka_message_base,
        payload=ScheduledEvent(
            **scheduler_event_base,
            schedule_type=ScheduleType.BATCH_START_TIME_MARGIN,
            schedule_margin=timestamp_future,
        ),
    )


@pytest.fixture
def batch_end_schedule(scheduler_kafka_message_base, scheduler_event_base):
    """Scheduler event with type BATCH_END_TIME"""
    return KafkaMessage(
        **scheduler_kafka_message_base,
        payload=ScheduledEvent(
            **scheduler_event_base,
            schedule_type=ScheduleType.BATCH_END_TIME,
        ),
    )


@pytest.fixture
def dataset_arrival_schedule(scheduler_kafka_message_base, schedule_dataset, timestamp_past, timestamp_now):
    """Scheduler event with type DATASET_ARRIVAL_MARGIN"""
    return KafkaMessage(
        **scheduler_kafka_message_base,
        payload=ScheduledEvent(
            schedule_id=schedule_dataset.id,
            component_id=schedule_dataset.component_id,
            schedule_timestamp=timestamp_past,
            schedule_margin=timestamp_now,
            schedule_type=ScheduleType.DATASET_ARRIVAL_MARGIN,
        ),
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "run_status",
    (
        RunStatus.MISSING,
        RunStatus.RUNNING,
        RunStatus.COMPLETED,
        RunStatus.COMPLETED_WITH_WARNINGS,
        RunStatus.FAILED,
    ),
)
def test_scheduler_run_should_start_no_pending(
    kafka_producer, kafka_consumer, pipeline, batch_start_schedule, run_status, pipeline_edge
):
    """Check that runs not marked pending are not touched when start schedule occurs"""
    key = None if run_status == RunStatus.MISSING else "some key"
    start_time = None if run_status == RunStatus.MISSING else datetime.now()
    run = Run.create(status=run_status.name, start_time=start_time, key=key, pipeline=pipeline)
    kafka_consumer.__iter__.return_value = iter((batch_start_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Run.select().get().status == run.status
    assert RunAlert.select().count() == 0
    assert Instance.select().count() == 0


@pytest.mark.integration
def test_scheduler_run_should_start_with_pending(
    kafka_producer, kafka_consumer, pipeline, batch_start_schedule, journey, pipeline_edge
):
    """Check that pending runs are marked missing when start schedule occurs"""
    instance = Instance.create(journey=journey)
    expected_start_time = datetime(2005, 3, 2, 2, 2, 2, tzinfo=timezone.utc)
    run = Run.create(
        status=RunStatus.PENDING.name,
        start_time=None,
        expected_start_time=expected_start_time,
        key=None,
        pipeline=pipeline,
        instance_set=InstanceSet.get_or_create([instance.id]),
    )

    kafka_consumer.__iter__.return_value = iter((batch_start_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Run.select().get().status == RunStatus.MISSING.name
    assert Run.select().get().start_time is None
    assert RunAlert.select().count() == 1
    alert = RunAlert.select().get()
    assert alert.run == run
    assert alert.level == AlertLevel.ERROR
    assert alert.type == RunAlertType.MISSING_RUN
    assert alert.description == RUN_ALERT_DESCRIPTIONS[RunAlertType.MISSING_RUN].format(name=pipeline.display_name)
    assert Instance.select().count() == 1
    assert Instance.get().status == InstanceStatus.ERROR.value

    # The created alert should have the expected_start_time value set
    assert alert.expected_start_time == expected_start_time

    counter = Counter(callargs[0][1].__class__ for callargs in kafka_producer.produce.call_args_list)
    assert counter[RunAlertEvent] == 1
    assert counter[InstanceAlertEvent] == 1
    for callargs in kafka_producer.produce.call_args_list:
        produced_event = callargs[0][1]
        if isinstance(produced_event, RunAlertEvent):
            assert produced_event.level == alert.level
            assert produced_event.type == alert.type
        elif isinstance(produced_event, InstanceAlertEvent):
            assert produced_event.type == InstanceAlertType.INCOMPLETE

    assert InstanceAlert.select().count() == 1
    assert InstanceAlert.get().type == InstanceAlertType.INCOMPLETE
    assert Instance.select().count() == 1
    instance = Instance.get()
    assert not instance.active
    assert instance.status == InstanceStatus.ERROR.value


@pytest.mark.integration
def test_scheduler_run_did_start(kafka_producer, kafka_consumer, pipeline, batch_start_margin_schedule, pipeline_edge):
    """Check that no pending run is created if run started at end of margin"""
    run = Run.create(
        status=RunStatus.COMPLETED.name,
        start_time=batch_start_margin_schedule.payload.schedule_timestamp,
        key="some key",
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_start_margin_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Run.select().get().status == run.status
    assert RunAlert.select().count() == 0
    assert Instance.select().count() == 0


@pytest.mark.integration
def test_scheduler_run_should_have_started(
    kafka_producer,
    kafka_consumer,
    pipeline,
    batch_start_margin_schedule,
    pipeline_edge,
    instance_instance_set,
    local_patched_instance_set,
):
    """Check that pending run is created if run did not start at end of margin"""
    Run.create(
        status=RunStatus.RUNNING.name,
        start_time=batch_start_margin_schedule.payload.schedule_timestamp - timedelta(seconds=1),
        key="some key",
        pipeline=pipeline,
    )
    missing_run = Run.create(
        status=RunStatus.MISSING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_start_margin_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.get_by_id(missing_run.id).status == RunStatus.MISSING.name
    assert Run.select().count() == 3

    run = Run.select().where(Run.status == RunStatus.PENDING.name).get()
    assert run.start_time is None
    assert Run.expected_start_time == batch_start_margin_schedule.payload.schedule_timestamp
    assert run.key is None
    assert run.pipeline == pipeline

    assert RunAlert.select().count() == 1
    alert = RunAlert.select().get()
    assert alert.level == AlertLevel.WARNING
    assert alert.type == RunAlertType.LATE_START
    assert alert.description == RUN_ALERT_DESCRIPTIONS[RunAlertType.LATE_START].format(name=pipeline.display_name)
    assert alert.run == run

    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type

    assert Instance.select().count() == 1
    instance = Instance.get()
    assert instance.active
    assert len(run.instance_set.iis) == 1
    assert instance.status == InstanceStatus.WARNING.value


@pytest.mark.integration
def test_scheduler_no_change_when_pipeline_is_deleted(kafka_producer, kafka_consumer, batch_start_margin_schedule):
    """Pipeline was removed so no pending run can be created"""
    batch_start_margin_schedule.payload.component_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((batch_start_margin_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 0
    assert RunAlert.select().count() == 0


@pytest.mark.integration
def test_scheduler_run_should_have_ended(
    kafka_producer, kafka_consumer, pipeline, batch_end_schedule, pipeline_edge, run_status_message
):
    """Check that "ended late" alert is created at end schedule if newest run did not end"""
    # Old runs
    Run.create(
        status=RunStatus.COMPLETED.name,
        start_time=batch_end_schedule.payload.schedule_timestamp - timedelta(seconds=1),
        end_time=batch_end_schedule.payload.schedule_margin,
        key="some key",
        pipeline=pipeline,
    )
    Run.create(
        status=RunStatus.MISSING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
    )
    # New run
    run = Run.create(
        status=RunStatus.RUNNING.name,
        start_time=batch_end_schedule.payload.schedule_timestamp,
        key="some other key",
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 3
    assert RunAlert.select().count() == 1
    alert = RunAlert.select().get()
    assert alert.level == AlertLevel.WARNING
    assert alert.type == RunAlertType.LATE_END
    assert alert.description == RUN_ALERT_DESCRIPTIONS[RunAlertType.LATE_END].format(name=pipeline.display_name)
    assert alert.run == run

    # The created alert should have the expected_end_time value set
    assert alert.expected_end_time == batch_end_schedule.payload.schedule_timestamp

    # The run should have been updated with the expected_end_time value set
    updated_run = Run.get_by_id(run.id)
    assert updated_run.expected_end_time == batch_end_schedule.payload.schedule_timestamp

    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
def test_scheduler_mark_pending_as_ended_late(kafka_producer, kafka_consumer, pipeline, batch_end_schedule):
    """Check that a pending run is marked late"""
    Run.create(
        status=RunStatus.RUNNING.name,
        key="some key",
        pipeline=pipeline,
    )
    Run.create(
        status=RunStatus.MISSING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
    )
    run = Run.create(
        status=RunStatus.PENDING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 3
    assert RunAlert.select().count() == 1
    alert = RunAlert.select().get()
    assert alert.level == AlertLevel.WARNING
    assert alert.type == RunAlertType.LATE_END
    assert alert.description == RUN_ALERT_DESCRIPTIONS[RunAlertType.LATE_END].format(name=pipeline.display_name)
    assert alert.run == run
    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
def test_scheduler_mark_newest_open_run_as_late(kafka_producer, kafka_consumer, pipeline, batch_end_schedule):
    """Mark the run that started last as late when there are multiple active runs"""
    Run.create(
        status=RunStatus.RUNNING.name,
        key="some key",
        pipeline=pipeline,
    )
    run = Run.create(
        status=RunStatus.RUNNING.name,
        key="some other key",
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 2
    assert RunAlert.select().count() == 1
    alert = RunAlert.select().get()
    assert alert.level == AlertLevel.WARNING
    assert alert.type == RunAlertType.LATE_END
    assert alert.description == RUN_ALERT_DESCRIPTIONS[RunAlertType.LATE_END].format(name=pipeline.display_name)
    assert alert.run == run
    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
def test_scheduler_mark_run_ended_too_late_as_late(kafka_producer, kafka_consumer, pipeline, batch_end_schedule):
    """Mark the run as late if the end time is after (or equal) to schedule timestamp"""
    run = Run.create(
        status=RunStatus.COMPLETED.name,
        start_time=batch_end_schedule.payload.schedule_timestamp - timedelta(seconds=2),
        end_time=batch_end_schedule.payload.schedule_timestamp,
        key="some other key",
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert RunAlert.select().count() == 1
    alert = RunAlert.select().get()
    assert alert.level == AlertLevel.WARNING
    assert alert.type == RunAlertType.LATE_END
    assert alert.description == RUN_ALERT_DESCRIPTIONS[RunAlertType.LATE_END].format(name=pipeline.display_name)
    assert alert.run == run
    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
def test_scheduler_run_did_end(kafka_producer, kafka_consumer, pipeline, batch_end_schedule):
    """Check that no "ended late" alert is created when run ended in time"""
    Run.create(
        status=RunStatus.COMPLETED.name,
        start_time=batch_end_schedule.payload.schedule_timestamp - timedelta(seconds=2),
        end_time=batch_end_schedule.payload.schedule_timestamp - timedelta(seconds=1),
        key="some key",
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert RunAlert.select().count() == 0


@pytest.mark.integration
def test_scheduler_mark_late_only_once(kafka_producer, kafka_consumer, pipeline, batch_end_schedule):
    """A run that is running but was already marked late is not marked again"""
    run = Run.create(
        status=RunStatus.RUNNING.name,
        key="some key",
        pipeline=pipeline,
    )
    RunAlert.create(run=run, description="asdf", message="", level=AlertLevel.WARNING, type=RunAlertType.LATE_END)
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert RunAlert.select().count() == 1


@pytest.mark.integration
def test_scheduler_dont_mark_missed_late(kafka_producer, kafka_consumer, pipeline, batch_end_schedule):
    """Missed runs are never marked late"""
    Run.create(
        status=RunStatus.MISSING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
    )
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert RunAlert.select().count() == 0


@pytest.mark.integration
def test_scheduler_map_run_status_to_pending_run(
    kafka_producer, kafka_consumer, pipeline, run_status_message, journey, pipeline_edge
):
    """Check that pending run is marked running when it starts"""
    Run.create(
        status=RunStatus.RUNNING.name,
        key=run_status_message.payload.run_key + "-testsuffix",
        pipeline=pipeline,
    )
    Instance.create(journey=journey)
    run = Run.create(
        status=RunStatus.PENDING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
    )

    run_status_message.payload.status = RunStatus.COMPLETED.name
    run_status_message.payload.pipeline_key = pipeline.key
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 2
    assert Run.get_by_id(run.id).status == RunStatus.COMPLETED.name
    assert RunAlert.select().count() == 0
    assert Instance.select().count() == 1
    assert InstancesInstanceSets.select().count() == 1


@pytest.mark.integration
def test_scheduler_map_test_outcomes_to_pending_run(
    kafka_producer, kafka_consumer, pipeline, test_outcomes_message, journey, pipeline_edge
):
    """Check that pending run is marked running when it starts"""
    Run.create(
        status=RunStatus.RUNNING.name,
        key=test_outcomes_message.payload.run_key + "-testsuffix",
        pipeline=pipeline,
    )
    instance = Instance.create(journey=journey)
    run = Run.create(
        status=RunStatus.PENDING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
        instance_set=InstanceSet.get_or_create([instance.id]),
    )

    test_outcomes_message.payload.pipeline_key = pipeline.key
    test_outcomes_message.payload.task_key = None
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 2
    assert Run.get_by_id(run.id).status == RunStatus.RUNNING.name
    assert RunAlert.select().count() == 0
    assert Instance.select().count() == 1
    assert InstancesInstanceSets.select().count() == 1


@pytest.mark.integration
def test_scheduler_map_run_status_to_existing_run_key(
    kafka_producer, kafka_consumer, pipeline, run_status_message, journey, pipeline_edge
):
    """Check that a run event maps to a run with a matching key instead of a pending run"""
    instance = Instance.create(journey=journey)
    run_key = "this key"
    Run.create(
        status=RunStatus.RUNNING.name,
        key=run_key,
        pipeline=pipeline,
        instance_set=InstanceSet.get_or_create([instance.id]),
    )
    run = Run.create(
        status=RunStatus.PENDING.name,
        start_time=None,
        key=None,
        pipeline=pipeline,
    )
    run_status_message.payload.pipeline_key = pipeline.key
    run_status_message.payload.run_key = run_key
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 2
    assert Run.get_by_id(run.id).status == RunStatus.PENDING.name
    assert RunAlert.select().count() == 0
    assert Instance.select().count() == 1
    assert InstancesInstanceSets.select().count() == 1


@pytest.mark.integration
@pytest.mark.parametrize("pre_existing_instance", (False, True))
def test_dataset_arrival_operation_does_not_exist(
    pre_existing_instance, kafka_producer, kafka_consumer, dataset_arrival_schedule, dataset_edge
):
    if pre_existing_instance:
        Instance.create(journey=dataset_edge.journey)

    kafka_consumer.__iter__.return_value = iter((dataset_arrival_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == 1
    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.select().get()
    assert alert.type == InstanceAlertType.DATASET_NOT_READY
    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
@pytest.mark.parametrize("time_delta", (timedelta(hours=-1), timedelta(hours=1)))
def test_dataset_arrival_operation_outside_window(
    time_delta, kafka_producer, kafka_consumer, dataset_arrival_schedule, dataset_edge, timestamp_now
):
    DatasetOperation.create(
        dataset=dataset_edge.right,
        operation_time=timestamp_now + time_delta,
        operation=DatasetOperationType.WRITE,
    )

    kafka_consumer.__iter__.return_value = iter((dataset_arrival_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == 1
    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.select().get()
    assert alert.type == InstanceAlertType.DATASET_NOT_READY
    alert_event = kafka_producer.produce.call_args_list[-1][0][1]
    assert alert_event.level == alert.level
    assert alert_event.type == alert.type


@pytest.mark.integration
@pytest.mark.parametrize(
    "dataset_operation_type,alert_count", ((DatasetOperationType.READ, 1), (DatasetOperationType.WRITE, 0))
)
def test_dataset_arrival_operation_within_window(
    kafka_producer,
    kafka_consumer,
    dataset_operation_message,
    dataset_operation_type,
    alert_count,
    dataset_arrival_schedule,
    dataset_edge,
    timestamp_now,
):
    DatasetOperation.create(
        dataset=dataset_edge.right,
        operation_time=timestamp_now - timedelta(seconds=1),
        operation=dataset_operation_type,
    )

    kafka_consumer.__iter__.return_value = iter((dataset_arrival_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == alert_count
    assert InstanceAlert.select().count() == alert_count
    if alert_count:
        alert = InstanceAlert.select().get()
        assert alert.type == InstanceAlertType.DATASET_NOT_READY
        alert_event = kafka_producer.produce.call_args_list[-1][0][1]
        assert alert_event.level == alert.level
        assert alert_event.type == alert.type


@pytest.mark.integration
def test_on_pending_run_start_check_out_of_sequence_alert(
    kafka_producer, kafka_consumer, pipeline, run_status_message, journey, simple_dag, pipeline2
):
    Run.create(
        status=RunStatus.RUNNING.name,
        key=run_status_message.payload.run_key + "-testsuffix",
        pipeline=pipeline,
    )
    instance = Instance.create(journey=journey)
    run = Run.create(
        status=RunStatus.PENDING.name,
        start_time=None,
        key=None,
        pipeline=pipeline2,
    )

    run_status_message.payload.pipeline_key = pipeline2.key
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 2
    assert Run.get_by_id(run.id).status == RunStatus.RUNNING.name
    assert InstanceAlert.select().where(InstanceAlert.type == InstanceAlertType.OUT_OF_SEQUENCE).count() == 1
    alert = InstanceAlert.get()
    assert alert.instance.id == instance.id


@pytest.mark.integration
def test_on_missing_run_skip_out_of_sequence_alert(
    kafka_producer, kafka_consumer, pipeline, run_status_message, journey, simple_dag, pipeline2, batch_start_schedule
):
    instance = Instance.create(journey=journey)
    Run.create(
        status=RunStatus.RUNNING.name,
        key=run_status_message.payload.run_key + "-testsuffix",
        pipeline=pipeline,
    )
    run = Run.create(
        status=RunStatus.PENDING.name,
        start_time=None,
        key=None,
        pipeline=pipeline2,
        instance_set=InstanceSet.get_or_create([instance.id]),
    )
    batch_start_schedule.payload.component_id = pipeline2.id
    kafka_consumer.__iter__.return_value = iter((batch_start_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 2
    assert Run.get(Run.id == run.id).status == RunStatus.MISSING.name
    assert InstanceAlert.select().where(InstanceAlert.type == InstanceAlertType.OUT_OF_SEQUENCE).count() == 0


@pytest.mark.integration
def test_scheduler_no_run_bulk_update_batch_end(kafka_producer, kafka_consumer, pipeline, batch_end_schedule):
    """Bulk update isn't run for `batch_end` when there are no runs to update."""
    kafka_consumer.__iter__.return_value = iter((batch_end_schedule,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()
    assert Run.select().count() == 0
