from datetime import datetime

import pytest

from common.datetime_utils import datetime_formatted
from rules_engine.actions.send_email_action import SendEmailAction
from testlib.fixtures import entities
from testlib.fixtures.v1_events import RUNNING_run_status_event, event_data  # noqa: F401

instance_alert_entity = entities.instance_alert
run_alert_entity = entities.run_alert


@pytest.mark.integration
def test_send_run_alert_email_datapoints(
    action, auth_provider, run_alert, run, project, pipeline, company, journey, rule
):
    """Email service can construct valid context for email templates from run alerts."""
    rule.action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action_executor = SendEmailAction(action, rule.action_args)
    context = action_executor._get_data_points(run_alert, rule, journey.id)

    assert context["run_key"] == run.key
    assert context["run_id"] == run.id
    assert context["event_timestamp_formatted"] == "May 10, 2023 at 01:04 AM (UTC)"
    assert context["project_id"] == project.id
    assert context["batch_pipeline_id"] == pipeline.id
    assert context["component_key"] == pipeline.key
    assert context["component_name"] == pipeline.name
    assert context["alert_type"] == run_alert.type.value
    assert context["alert_level"] == run_alert.level.value
    assert context["base_url"] == "testdomain.com"


@pytest.mark.integration
def test_send_run_alert_email_datapoints_no_run(
    action, auth_provider, run_alert, project, pipeline, company, journey, rule
):
    """When run not found in db, run_key is N/A."""
    rule.action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action_executor = SendEmailAction(action, rule.action_args)
    context = action_executor._get_data_points(run_alert, rule, journey.id)
    assert context["run_key"] == "N/A"


@pytest.mark.integration
def test_send_instance_alert_email_datapoints(
    action, auth_provider, instance_alert, project, pipeline, company, journey, rule
):
    """Email service can construct valid context for email templates from instance alerts."""
    rule.action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action_executor = SendEmailAction(action, rule.action_args)
    context = action_executor._get_data_points(instance_alert, rule, journey.id)

    assert context["event_timestamp_formatted"] == "May 10, 2023 at 01:04 AM (UTC)"
    assert context["project_id"] == project.id
    assert context["alert_type"] == instance_alert.type.value
    assert context["alert_level"] == instance_alert.level.value
    assert context["base_url"] == "testdomain.com"

    # There is no instance alert for the alert_id so these should be None
    assert context["run_expected_start_time"] is None
    assert context["run_expected_end_time"] is None

    assert "component_key" not in context  # Instance alerts should not have a component_key context variable


@pytest.mark.integration
def test_send_instance_alert_email_datapoints_start_end(
    action, auth_provider, instance_alert, instance_alert_entity, journey, rule
):
    """Email service context contains expected start/end details for instance alerts."""
    rule.action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action_executor = SendEmailAction(action, rule.action_args)
    context = action_executor._get_data_points(instance_alert, rule, journey.id)

    assert context["run_expected_start_time"] == "August 13, 2005 at 04:02 AM (UTC)"
    assert context["run_expected_end_time"] == "August 13, 2005 at 08:04 AM (UTC)"


@pytest.mark.integration
def test_send_run_alert_email_datapoints_start_end(action, auth_provider, run_alert, run_alert_entity, journey, rule):
    """Email service context contains expected start/end details for run alerts."""
    rule.action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action_executor = SendEmailAction(action, rule.action_args)
    context = action_executor._get_data_points(run_alert, rule, journey.id)

    assert context["run_expected_start_time"] == "August 13, 2005 at 04:02 AM (UTC)"
    assert context["run_expected_end_time"] == "August 13, 2005 at 08:04 AM (UTC)"


@pytest.mark.integration
def test_send_run_status_email_datapoints_start_end(
    action, auth_provider, RUNNING_run_status_event, run, journey, pipeline, rule
):
    """Email service context contains expected start/end details for run alerts."""
    RUNNING_run_status_event.component_id = pipeline.id
    RUNNING_run_status_event.run_id = run.id
    run.expected_start_time = datetime.utcnow()
    run.expected_end_time = datetime.utcnow()
    run.save()
    rule.action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action_executor = SendEmailAction(action, rule.action_args)

    context = action_executor._get_data_points(RUNNING_run_status_event, rule, journey.id)

    assert context["run_expected_start_time"] == datetime_formatted(run.expected_start_time)
    assert context["run_expected_end_time"] == datetime_formatted(run.expected_end_time)
