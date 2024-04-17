from datetime import datetime, timezone

import pytest

from common.entities import AlertLevel, InstanceAlert, InstanceAlertType, RunAlert, RunAlertType


@pytest.mark.integration
def test_instance_alert_create_valid(instance):
    inst = InstanceAlert.create(
        instance=instance,
        name="SomeAlert",
        description="Some cool alert",
        message="An Alert was generated",
        level=AlertLevel.WARNING,
        type=InstanceAlertType.OUT_OF_SEQUENCE,
    )
    assert inst
    inst.save()


@pytest.mark.integration
def test_instance_alert_create_invalid_level(instance):
    with pytest.raises(ValueError):
        InstanceAlert.create(
            instance=instance,
            name="SomeAlert",
            description="Some cool alert",
            message="An Alert was generated",
            level="invalid",
            type=InstanceAlertType.OUT_OF_SEQUENCE,
        )


@pytest.mark.integration
def test_instance_alert_create_invalid_type(instance):
    with pytest.raises(ValueError):
        InstanceAlert.create(
            instance=instance,
            name="SomeAlert",
            description="Some cool alert",
            message="An Alert was generated",
            level=AlertLevel.WARNING,
            type="invalid",
        )


@pytest.mark.integration
def test_run_alert_create_valid(pipeline_run):
    runalert = RunAlert.create(
        run=pipeline_run,
        name="SomeAlert",
        description="Some cool alert",
        level=AlertLevel.ERROR,
        type=RunAlertType.UNEXPECTED_STATUS_CHANGE,
    )
    assert runalert
    runalert.save()


@pytest.mark.integration
def test_run_alert_create_invalid_level(pipeline_run):
    with pytest.raises(ValueError):
        RunAlert.create(
            run=pipeline_run,
            name="SomeAlert",
            description="Some cool alert",
            level="invalid",
            type=RunAlertType.UNEXPECTED_STATUS_CHANGE,
        )


@pytest.mark.integration
def test_run_alert_create_invalid_type(pipeline_run):
    with pytest.raises(ValueError):
        RunAlert.create(
            run=pipeline_run,
            name="SomeAlert",
            description="Some cool alert",
            level=AlertLevel.ERROR,
            type="invalid",
        )


@pytest.mark.integration
def test_run_alert_expected_start_time_set(pipeline_run):
    run_alert = RunAlert(run=pipeline_run, name="A", description="A", level=AlertLevel.ERROR, type="invalid")
    run_alert.expected_start_time = datetime(2005, 8, 13, 8, 42, 24)
    assert run_alert.details["expected_start_time"] == 1123922544.0


@pytest.mark.integration
def test_run_alert_expected_start_time_get(pipeline_run):
    run_alert = RunAlert(run=pipeline_run, name="A", description="A", level=AlertLevel.ERROR, type="invalid")
    assert run_alert.expected_start_time is None
    run_alert.details["expected_start_time"] = 1123922544.0
    assert datetime(2005, 8, 13, 8, 42, 24, tzinfo=timezone.utc) == run_alert.expected_start_time


@pytest.mark.integration
def test_run_alert_expected_start_time_value_error(pipeline_run):
    run_alert = RunAlert(run=pipeline_run, name="A", description="A", level=AlertLevel.ERROR, type="invalid")
    run_alert.details["expected_start_time"] = object()
    with pytest.raises(ValueError):
        run_alert.expected_start_time


@pytest.mark.integration
def test_run_alert_expected_end_time_set(pipeline_run):
    run_alert = RunAlert(run=pipeline_run, name="A", description="A", level=AlertLevel.ERROR, type="invalid")
    run_alert.expected_end_time = datetime(2005, 8, 13, 8, 42, 24)
    assert run_alert.details["expected_end_time"] == 1123922544.0


@pytest.mark.integration
def test_run_alert_expected_end_time_get(pipeline_run):
    run_alert = RunAlert(run=pipeline_run, name="A", description="A", level=AlertLevel.ERROR, type="invalid")
    assert run_alert.expected_end_time is None  # No details have been added yet
    run_alert.details["expected_end_time"] = 1123922544.0
    assert datetime(2005, 8, 13, 8, 42, 24, tzinfo=timezone.utc) == run_alert.expected_end_time


@pytest.mark.integration
def test_run_alert_expected_end_time_value_error(pipeline_run):
    run_alert = RunAlert(run=pipeline_run, name="A", description="A", level=AlertLevel.ERROR, type="invalid")
    run_alert.details["expected_end_time"] = object()
    with pytest.raises(ValueError):
        run_alert.expected_end_time


@pytest.mark.integration
def test_run_alert_expected_times_naive(pipeline_run):
    run_alert = RunAlert(run=pipeline_run, name="A", description="A", level=AlertLevel.ERROR, type="invalid")
    run_alert.expected_start_time = datetime(2005, 8, 13, 8, 42, 24)
    run_alert.expected_end_time = datetime(2005, 8, 13, 8, 55, 24)

    assert run_alert.expected_start_time == datetime(2005, 8, 13, 8, 42, 24, tzinfo=timezone.utc)
    assert run_alert.expected_end_time == datetime(2005, 8, 13, 8, 55, 24, tzinfo=timezone.utc)


@pytest.mark.integration
def test_instance_alert_expected_start_time_set(instance):
    instance_alert = InstanceAlert(
        instance=instance, name="A", description="A", message="A", level=AlertLevel.WARNING, type="invalid"
    )
    instance_alert.expected_start_time = datetime(2005, 8, 13, 8, 42, 24)
    assert instance_alert.details["expected_start_time"] == 1123922544.0


@pytest.mark.integration
def test_instance_alert_expected_start_time_get(instance):
    instance_alert = InstanceAlert(
        instance=instance, name="A", description="A", message="A", level=AlertLevel.WARNING, type="invalid"
    )
    instance_alert.details["expected_start_time"] = 1123922544.0
    assert datetime(2005, 8, 13, 8, 42, 24, tzinfo=timezone.utc) == instance_alert.expected_start_time


@pytest.mark.integration
def test_instance_alert_expected_end_time_set(instance):
    instance_alert = InstanceAlert(
        instance=instance, name="A", description="A", message="A", level=AlertLevel.WARNING, type="invalid"
    )
    instance_alert.expected_end_time = datetime(2005, 8, 13, 8, 42, 24)
    assert instance_alert.details["expected_end_time"] == 1123922544.0


@pytest.mark.integration
def test_instance_alert_expected_end_time_get(instance):
    instance_alert = InstanceAlert(
        instance=instance, name="A", description="A", message="A", level=AlertLevel.WARNING, type="invalid"
    )
    instance_alert.details["expected_end_time"] = 1123922544.0
    assert datetime(2005, 8, 13, 8, 42, 24, tzinfo=timezone.utc) == instance_alert.expected_end_time


@pytest.mark.integration
def test_instance_alert_expected_times_naive(instance):
    """Expected start/end times set with a naive datetime object are returned tzaware."""
    instance_alert = InstanceAlert(
        instance=instance, name="A", description="A", message="A", level=AlertLevel.WARNING, type="invalid"
    )
    instance_alert.expected_start_time = datetime(2005, 8, 13, 8, 42, 24)
    instance_alert.expected_end_time = datetime(2005, 8, 13, 8, 55, 24)

    assert instance_alert.expected_start_time == datetime(2005, 8, 13, 8, 42, 24, tzinfo=timezone.utc)
    assert instance_alert.expected_end_time == datetime(2005, 8, 13, 8, 55, 24, tzinfo=timezone.utc)


@pytest.mark.integration
def test_alert_expected_can_set_null(pipeline_run):
    run_alert = RunAlert(
        run=pipeline_run,
        name="A",
        description="A",
        level=AlertLevel.ERROR,
        type="invalid",
        details={"expected_start_time": 1123920721.0, "expected_end_time": 1123922544.0},
    )
    assert isinstance(run_alert.expected_start_time, datetime)
    assert isinstance(run_alert.expected_end_time, datetime)

    run_alert.expected_start_time = None
    assert "expected_start_time" not in run_alert.details

    run_alert.expected_end_time = None
    assert "expected_end_time" not in run_alert.details
