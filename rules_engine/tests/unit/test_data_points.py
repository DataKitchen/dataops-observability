from datetime import datetime, timezone

import pytest

from common.datetime_utils import datetime_formatted
from common.entities.component import ComponentType
from common.entities.rule import RunState
from common.events.v1 import ApiRunStatus, MessageEventLogLevel, MessageLogEvent, MetricLogEvent, RunStatusEvent
from common.actions.data_points import AlertDataPoints, DataPoints


@pytest.fixture
def run_status_event():
    return RunStatusEvent.as_event_from_request(
        {
            "status": ApiRunStatus.FAILED.name,
            "external_url": "http://asdf.com",
            "pipeline_key": "P1",
            "run_key": "R1",
        }
    )


@pytest.fixture
def message_log_event():
    return MessageLogEvent.as_event_from_request(
        {
            "log_level": MessageEventLogLevel.INFO.name,
            "message": "some message",
            "pipeline_key": "P1",
            "run_key": "R1",
        }
    )


@pytest.fixture
def metric_log_event():
    return MetricLogEvent.as_event_from_request(
        {"metric_key": "some key", "metric_value": 1, "dataset_key": "asdf", "run_key": "qwer"}
    )


@pytest.fixture
def data_point_namespaces():
    return {
        "event",
        "pipeline",
        "project",
        "rule",
        "run",
        "run_task",
        "task",
        "company",
        "component",
    }


@pytest.mark.unit
def test_data_points_functions(data_point_namespaces, run_status_event, rule):
    dps = DataPoints(run_status_event, rule)
    assert len(dps) == len(data_point_namespaces)
    assert dps.keys() == data_point_namespaces
    assert dps[next(iter(data_point_namespaces))]
    for dp in dps:
        assert dp in data_point_namespaces
    for ns in data_point_namespaces:
        assert ns in data_point_namespaces


@pytest.mark.unit
def test_event_data_points(run_status_event, message_log_event, metric_log_event, rule):
    dps = DataPoints(run_status_event, rule)
    assert dps.event.id == run_status_event.event_id
    assert dps.event.event_timestamp == run_status_event.event_timestamp.isoformat()
    assert dps.event.event_timestamp_formatted == datetime_formatted(run_status_event.event_timestamp)
    assert dps.event.received_timestamp == run_status_event.received_timestamp.isoformat()
    assert dps.event.received_timestamp_formatted == datetime_formatted(run_status_event.received_timestamp)
    assert dps.event.external_url == run_status_event.external_url
    run_status_event.external_url = None
    assert dps.event.external_url == "N/A"
    assert DataPoints(message_log_event, rule).event.log_level == message_log_event.log_level
    assert DataPoints(message_log_event, rule).event.message == message_log_event.message
    assert DataPoints(metric_log_event, rule).event.metric_key == metric_log_event.metric_key
    assert DataPoints(metric_log_event, rule).event.metric_value == metric_log_event.metric_value
    with pytest.raises(AttributeError):
        assert dps.event.status


@pytest.mark.unit
def test_project_data_points(run_status_event, project, rule):
    dps = DataPoints(run_status_event, rule)
    with pytest.raises(AttributeError):
        dps.project.name

    run_status_event.project_id = project.id
    assert dps.project.id == project.id
    assert dps.project.name == project.name


@pytest.mark.unit
def test_pipeline_data_points(run_status_event, pipeline, rule):
    run_status_event.pipeline_id = pipeline.id
    dps = DataPoints(run_status_event, rule)
    assert dps.pipeline.id == run_status_event.pipeline_id
    assert dps.pipeline.key == run_status_event.pipeline_key
    assert dps.pipeline.name == pipeline.name


@pytest.mark.unit
def test_instance_alert_datapoint(project, auth_provider, company, instance_alert, rule):
    dps = AlertDataPoints(instance_alert, rule)
    assert dps.event.id == instance_alert.event_id
    assert dps.event.event_timestamp_formatted == "May 10, 2023 at 01:04 AM (UTC)"
    assert dps.event.event_timestamp == "2023-05-10T01:04:02+00:00"
    assert dps.project.id == project.id
    assert dps.project.name == project.name
    assert dps.company.ui_url == "testdomain.com"


@pytest.mark.unit
def test_run_alert_datapoint(project, auth_provider, company, run, run_alert, rule):
    dps = AlertDataPoints(run_alert, rule)
    assert dps.run.id == run.id
    assert dps.run.key == run.key
    assert dps.run.name == run.name
    assert dps.event.id == run_alert.event_id
    assert dps.event.event_timestamp_formatted == "May 10, 2023 at 01:04 AM (UTC)"
    assert dps.event.event_timestamp == "2023-05-10T01:04:02+00:00"
    assert dps.project.id == project.id
    assert dps.project.name == project.name
    assert dps.company.ui_url == "testdomain.com"


@pytest.mark.unit
def test_rule_datapoint_alert_event(project, auth_provider, company, run, run_alert, rule):
    dps = AlertDataPoints(run_alert, rule)
    assert dps.rule.run_state_matches == None
    assert dps.rule.run_state_count == None
    assert dps.rule.run_state_group_run_name == None
    assert dps.rule.run_state_trigger_successive == None

    rule.rule_data = {
        "conditions": [
            {
                "run_state": {
                    "matches": RunState.LATE_START.name,
                    "trigger_successive": True,
                    "count": 2,
                    "group_run_name": True,
                }
            }
        ]
    }
    dps = AlertDataPoints(run_alert, rule)
    assert dps.rule.run_state_matches == RunState.LATE_START.name
    assert dps.rule.run_state_count == "2"
    assert dps.rule.run_state_group_run_name == "True"
    assert dps.rule.run_state_trigger_successive == "True"


@pytest.mark.unit
def test_rule_datapoint_runstatus_event(project, auth_provider, company, run, run_status_event, rule):
    dps = DataPoints(run_status_event, rule)
    assert dps.rule.run_state_matches == None
    assert dps.rule.run_state_count == None
    assert dps.rule.run_state_group_run_name == None
    assert dps.rule.run_state_trigger_successive == None

    rule.rule_data = {
        "conditions": [
            {
                "run_state": {
                    "matches": RunState.LATE_START.name,
                    "trigger_successive": True,
                    "count": 2,
                    "group_run_name": True,
                }
            }
        ]
    }
    dps = DataPoints(run_status_event, rule)
    assert dps.rule.run_state_matches == RunState.LATE_START.name
    assert dps.rule.run_state_count == "2"
    assert dps.rule.run_state_group_run_name == "True"
    assert dps.rule.run_state_trigger_successive == "True"


@pytest.mark.unit
def test_component_data_points(metric_log_event, dataset, rule):
    metric_log_event.component_id = dataset.id
    dps = DataPoints(metric_log_event, rule)
    assert dps.component.id == metric_log_event.dataset_id
    assert dps.component.key == metric_log_event.dataset_key
    assert dps.component.type == ComponentType.DATASET.name
    assert dps.component.name == dataset.name


@pytest.mark.unit
def test_run_data_points(run_status_event, run, rule):
    run_status_event.run_id = run.id
    dps = DataPoints(run_status_event, rule)
    assert dps.run.id == run_status_event.run_id
    assert dps.run.key == run_status_event.run_key

    # Since the decision is to use the run entity status, not the event status, check that they differ to know that
    # DataPoints is using the correct source
    assert run.status != run_status_event.status
    assert dps.run.status == run.status
    assert dps.run.start_time == run.start_time.replace(tzinfo=timezone.utc).isoformat()
    assert dps.run.start_time_formatted == datetime_formatted(run.start_time)
    assert dps.run.end_time == "N/A"
    assert dps.run.end_time_formatted == "N/A"
    assert dps.run.expected_start_time == None
    assert dps.run.expected_end_time == None


@pytest.mark.unit
def test_run_data_points_with_end_time(run_status_event, run, rule):
    run_status_event.run_id = run.id
    run.end_time = datetime.utcnow()
    run.save()
    dps = DataPoints(run_status_event, rule)
    # These are tested in a separate function because the run is cached in Event
    assert dps.run.end_time == run.end_time.replace(tzinfo=timezone.utc).isoformat()
    assert dps.run.end_time_formatted == datetime_formatted(run.end_time)


@pytest.mark.unit
def test_task_data_points(run_status_event, task, rule):
    run_status_event.task_id = task.id
    run_status_event.task_key = "a task key"
    dps = DataPoints(run_status_event, rule)
    assert dps.task.id == run_status_event.task_id
    assert dps.task.key == run_status_event.task_key
    assert dps.task.name == task.name


@pytest.mark.unit
def test_run_task_data_points(run_status_event, run_task, rule):
    run_status_event.run_task_id = run_task.id
    dps = DataPoints(run_status_event, rule)
    assert dps.run_task.id == run_status_event.run_task_id

    # Since the decision is to use the run task entity status, not the event status, check that they differ to know
    # that DataPoints is using the correct source
    assert run_task.status != run_status_event.status
    assert dps.run_task.status == run_task.status

    assert dps.run_task.start_time == "N/A"
    assert dps.run_task.start_time_formatted == "N/A"
    assert dps.run_task.end_time == "N/A"
    assert dps.run_task.end_time_formatted == "N/A"


@pytest.mark.unit
def test_run_task_data_points_with_times(run_status_event, run_task, rule):
    run_status_event.run_task_id = run_task.id
    run_task.start_time = datetime.utcnow()
    run_task.end_time = datetime.utcnow()
    run_task.save()
    dps = DataPoints(run_status_event, rule)
    # These are tested in a separate function because the run task is cached in Event
    assert dps.run_task.start_time == run_task.start_time.replace(tzinfo=timezone.utc).isoformat()
    assert dps.run_task.start_time_formatted == datetime_formatted(run_task.start_time)
    assert dps.run_task.end_time == run_task.end_time.replace(tzinfo=timezone.utc).isoformat()
    assert dps.run_task.end_time_formatted == datetime_formatted(run_task.end_time)


@pytest.mark.unit
def test_company_data_points(run_status_event, project, auth_provider, rule):
    run_status_event.project_id = project.id
    dps = DataPoints(run_status_event, rule)
    assert dps.company.ui_url == auth_provider.domain
