from uuid import uuid4

import pytest

from common.entities import Instance, InstanceAlertType, Run, RunAlertType
from common.entities.instance import InstanceStatus
from run_manager.alerts import create_instance_alert, create_run_alert
from run_manager.run_manager import RunManager


@pytest.mark.integration
@pytest.mark.parametrize(
    "alerts, expected_status, has_errors_flg, has_warnings_flg",
    [
        ([RunAlertType.COMPLETED_WITH_WARNINGS], InstanceStatus.WARNING.value, False, True),
        ([RunAlertType.LATE_START, RunAlertType.LATE_END], InstanceStatus.WARNING.value, False, True),
        ([RunAlertType.UNEXPECTED_STATUS_CHANGE, RunAlertType.MISSING_RUN], InstanceStatus.ERROR.value, True, True),
        ([RunAlertType.FAILED], InstanceStatus.ERROR.value, True, False),
        ([RunAlertType.FAILED, RunAlertType.MISSING_RUN], InstanceStatus.ERROR.value, True, False),
        ([RunAlertType.FAILED, RunAlertType.UNEXPECTED_STATUS_CHANGE], InstanceStatus.ERROR.value, True, True),
    ],
    ids=[
        "single warning alert",
        "consecutive warning alerts",
        "warning alert follow by error alert",
        "single error alert",
        "consecutive error alerts",
        "error alert follow by warning alert",
    ],
)
def test_run_manager_create_run_alerts(
    pipeline, run, instance_instance_set, alerts, expected_status, has_errors_flg, has_warnings_flg
):
    run.update(instance_set=instance_instance_set.instance_set).execute()
    for alert in alerts:
        create_run_alert(alert, run, pipeline)
    instance = Instance.get()
    assert instance.has_errors is has_errors_flg
    assert instance.has_warnings is has_warnings_flg
    assert instance.status == expected_status


@pytest.mark.integration
@pytest.mark.parametrize(
    "alerts, expected_status, has_errors_flg, has_warnings_flg",
    [
        ([InstanceAlertType.DATASET_NOT_READY], InstanceStatus.WARNING.value, False, True),
        (
            [InstanceAlertType.DATASET_NOT_READY, InstanceAlertType.TESTS_HAD_WARNINGS],
            InstanceStatus.WARNING.value,
            False,
            True,
        ),
        ([InstanceAlertType.DATASET_NOT_READY, InstanceAlertType.TESTS_FAILED], InstanceStatus.ERROR.value, True, True),
        ([InstanceAlertType.INCOMPLETE], InstanceStatus.ERROR.value, True, False),
        ([InstanceAlertType.OUT_OF_SEQUENCE, InstanceAlertType.TESTS_FAILED], InstanceStatus.ERROR.value, True, False),
        (
            [InstanceAlertType.OUT_OF_SEQUENCE, InstanceAlertType.DATASET_NOT_READY],
            InstanceStatus.ERROR.value,
            True,
            True,
        ),
    ],
    ids=[
        "single warning alert",
        "consecutive warning alerts",
        "warning alert follow by error alert",
        "single error alert",
        "consecutive error alerts",
        "error alert follow by warning alert",
    ],
)
def test_run_manager_create_instance_alerts(instance, alerts, expected_status, has_errors_flg, has_warnings_flg):
    for alert in alerts:
        create_instance_alert(alert, instance)
    instance = Instance.get()
    assert instance.status == expected_status
    assert instance.has_errors is has_errors_flg
    assert instance.has_warnings is has_warnings_flg


@pytest.mark.integration
def test_run_manager_instance_status_active(
    kafka_consumer,
    kafka_producer,
    run_status_message,
    pipeline_edge,
):
    run_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Instance.select().count() == 1
    instance = Instance.get()
    assert instance.active is True
    assert instance.has_errors is False
    assert instance.has_warnings is False
    assert instance.status == InstanceStatus.ACTIVE.value


@pytest.mark.integration
def test_run_manager_instance_status_complete(
    kafka_consumer,
    kafka_producer,
    run_status_message,
    completed_run_message,
    project,
    pipeline_edge,
):
    run_status_message.payload.event_id = uuid4()
    completed_run_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message, completed_run_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Instance.select().count() == 1
    instance = Instance.get()
    assert instance.active is False
    assert instance.has_errors is False
    assert instance.has_warnings is False
    assert instance.status == InstanceStatus.COMPLETED.value


@pytest.mark.integration
@pytest.mark.parametrize(
    "alert, expected_status",
    [
        (RunAlertType.LATE_START, InstanceStatus.WARNING.value),
        (RunAlertType.MISSING_RUN, InstanceStatus.ERROR.value),
        (InstanceAlertType.DATASET_NOT_READY, InstanceStatus.WARNING.value),
        (InstanceAlertType.INCOMPLETE, InstanceStatus.ERROR.value),
    ],
)
def test_run_manager_completed_run_with_alert(
    kafka_consumer,
    kafka_producer,
    run_status_message,
    completed_run_message,
    project,
    pipeline,
    pipeline_edge,
    alert,
    expected_status,
):
    # Instance ended with any alerts will have either ERROR or WARNING status, not COMPLETED
    run_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()
    assert Instance.select().count() == 1
    instance = Instance.get()
    assert instance.status == InstanceStatus.ACTIVE.value
    assert Run.select().count() == 1

    run = Run.get()
    create_run_alert(alert, run, pipeline) if alert in RunAlertType else create_instance_alert(alert, instance)

    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_key = pipeline.key
    completed_run_message.payload.run_key = run.key
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()
    instance = Instance.get()
    assert instance.status == expected_status
    assert instance.active is False
    assert instance.has_errors is (expected_status == InstanceStatus.ERROR.value)
    assert instance.has_warnings is (expected_status == InstanceStatus.WARNING.value)
