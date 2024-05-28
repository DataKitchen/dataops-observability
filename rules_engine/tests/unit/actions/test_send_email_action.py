from unittest.mock import Mock, PropertyMock, patch
from uuid import uuid4

import pytest
from peewee import DoesNotExist

from common.datetime_utils import datetime_formatted
from common.entities import AuthProvider
from common.entity_services.helpers import Page
from rules_engine.actions.send_email_action import SendEmailAction


@pytest.fixture()
def send_email_mock():
    with patch("common.email.email_service.EmailService.send_email", return_value={"MessageId": 1}) as send_email_mock:
        yield send_email_mock


@pytest.fixture()
def journey_mock():
    journey_mock = Mock()
    journey_mock.name = "test journey name"
    with patch("rules_engine.actions.send_email_action.Journey.get_by_id", return_value=journey_mock):
        yield journey_mock


@pytest.fixture()
def rule_mock():
    rule_mock = Mock()
    yield rule_mock


@pytest.fixture()
def auth_provider_domain():
    return "authprovider.com"


@pytest.fixture()
def project_service(auth_provider_domain):
    with patch(
        "rules_engine.data_points.ProjectService.get_auth_providers_with_rules",
        return_value=Page[AuthProvider](results=[AuthProvider(domain=auth_provider_domain)], total=1),
    ) as get_auth_providers:
        yield get_auth_providers


@pytest.mark.unit
def test_send_email_constructor(action):
    rule_action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action_executor = SendEmailAction(action, rule_action_args)
    assert action_executor.arguments == {
        "template": "TestTemplateNested",
        "from_address": "test@domain.com",
        "recipients": ["a@example.com"],
    }
    assert action_executor.action_template == action


@pytest.mark.unit
@pytest.mark.parametrize("argument", ("template", "from_address", "recipients"))
def test_send_email_constructor_missing_action_argument(argument, action):
    rule_action_args = {"template": "TestTemplateNested", "recipients": ["a@example.com"]}
    action.action_args = {"from_address": "test@domain.com", "recipients": ["success@example.com"]}
    action.action_args.pop(argument, None)
    rule_action_args.pop(argument, None)
    with pytest.raises(ValueError):
        SendEmailAction(action, rule_action_args)


@pytest.mark.unit
def test_send_email_execute_ok(action, run_status_event, send_email_mock, project_service, journey_mock, rule_mock):
    email_to = "success@example.com"
    email_from = "test@domain.com"
    template_name = "TestTemplateNested"
    action_executor = SendEmailAction(
        action, {"from_address": email_from, "recipients": [email_to], "template": template_name, "smtp_config": {}}
    )
    result = action_executor.execute(run_status_event, rule_mock, uuid4())
    assert result is True
    send_email_mock.assert_called_once()


@pytest.mark.unit
def test_send_email_execute_fail(action, run_status_event, send_email_mock, project_service, journey_mock, rule_mock):
    email_to = "success@example.com"
    email_from = "test@domain.com"
    template_name = "TestTemplateNested"
    send_email_mock.side_effect = Exception({}, "")

    action_executor = SendEmailAction(
        action, {"from_address": email_from, "recipients": [email_to], "template": template_name, "smtp_config": {}}
    )
    result = action_executor.execute(run_status_event, rule_mock, uuid4())
    assert result is False
    send_email_mock.assert_called_once()


@pytest.mark.unit
def test_get_more_data_points_action_args_domain(
    action, run_status_event, project_service, auth_provider_domain, journey_mock, rule_mock
):
    # This test can be removed when we're sure that all action_args with "base_url" are gone.
    email_to = "success@example.com"
    email_from = "test@domain.com"
    template_name = "TestTemplateNested"
    base_url = "example.io"
    action = SendEmailAction(
        action, {"from_address": email_from, "recipients": [email_to], "template": template_name, "base_url": base_url}
    )

    expected_data_points = {
        **run_status_event.as_dict(),
        "journey_name": journey_mock.name,
        "component_name": run_status_event.component.display_name,
        "task_name": run_status_event.task.display_name,
        "component_key": run_status_event.pipeline_key,
        "base_url": auth_provider_domain,
        "project_name": run_status_event.project.name,
        "event_timestamp_formatted": datetime_formatted(run_status_event.event_timestamp),
        "run_task_start_time": datetime_formatted(run_status_event.run_task.start_time),
        "run_expected_start_time": None,
        "run_expected_end_time": None,
        "rule_consecutive_run_count": None,
        "rule_group_by_run_name": None,
        "rule_only_exact_count": None,
        "rule_run_state_matches": None,
    }
    actual_data_points = action._get_data_points(run_status_event, rule_mock, uuid4())
    assert actual_data_points == expected_data_points


@pytest.mark.unit
def test_get_more_data_points_no_start_time(
    action, run_status_event, project_service, auth_provider_domain, journey_mock, rule_mock
):
    # This test can be removed when we're sure that all action_args with "base_url" are gone.
    email_to = "success@example.com"
    email_from = "test@domain.com"
    template_name = "TestTemplateNested"
    base_url = "example.io"
    action = SendEmailAction(
        action, {"from_address": email_from, "recipients": [email_to], "template": template_name, "base_url": base_url}
    )
    run_status_event.run_task.start_time = None

    expected_data_points = {
        **run_status_event.as_dict(),
        "journey_name": journey_mock.name,
        "component_name": run_status_event.component.display_name,
        "task_name": run_status_event.task.display_name,
        "component_key": run_status_event.pipeline_key,
        "base_url": auth_provider_domain,
        "project_name": run_status_event.project.name,
        "event_timestamp_formatted": datetime_formatted(run_status_event.event_timestamp),
        "run_task_start_time": "N/A",
        "run_expected_start_time": None,
        "run_expected_end_time": None,
        "rule_consecutive_run_count": None,
        "rule_group_by_run_name": None,
        "rule_only_exact_count": None,
        "rule_run_state_matches": None,
    }
    actual_data_points = action._get_data_points(run_status_event, rule_mock, uuid4())
    assert actual_data_points == expected_data_points


@pytest.mark.unit
def test_get_more_data_points_auth_provider_domain(
    action, run_status_event, project_service, auth_provider_domain, journey_mock, rule_mock
):
    email_to = "success@example.com"
    email_from = "test@domain.com"
    template_name = "TestTemplateNested"
    action = SendEmailAction(action, {"from_address": email_from, "recipients": [email_to], "template": template_name})

    expected_data_points = {
        **run_status_event.as_dict(),
        "journey_name": journey_mock.name,
        "component_name": run_status_event.component.display_name,
        "task_name": run_status_event.task.display_name,
        "component_key": run_status_event.pipeline_key,
        "base_url": auth_provider_domain,
        "project_name": run_status_event.project.name,
        "event_timestamp_formatted": datetime_formatted(run_status_event.event_timestamp),
        "run_task_start_time": datetime_formatted(run_status_event.run_task.start_time),
        "run_expected_start_time": None,
        "run_expected_end_time": None,
        "rule_consecutive_run_count": None,
        "rule_group_by_run_name": None,
        "rule_only_exact_count": None,
        "rule_run_state_matches": None,
    }
    actual_data_points = action._get_data_points(run_status_event, rule_mock, uuid4())
    assert actual_data_points == expected_data_points


@pytest.mark.unit
def test_get_more_data_points_no_domain(
    action, mocked_test_outcomes_dataset_event, project_service, journey_mock, rule_mock
):
    email_to = "success@example.com"
    email_from = "test@domain.com"
    template_name = "TestTemplateNested"
    action = SendEmailAction(action, {"from_address": email_from, "recipients": [email_to], "template": template_name})
    project_service.return_value = Page(results=[], total=0)

    expected_data_points = {
        **mocked_test_outcomes_dataset_event.as_dict(),
        "journey_name": journey_mock.name,
        "component_name": mocked_test_outcomes_dataset_event.component.display_name,
        "task_name": mocked_test_outcomes_dataset_event.task.display_name,
        "component_key": mocked_test_outcomes_dataset_event.dataset_key,
        "base_url": "",
        "project_name": mocked_test_outcomes_dataset_event.project.name,
        "event_timestamp_formatted": datetime_formatted(mocked_test_outcomes_dataset_event.event_timestamp),
        "run_task_start_time": datetime_formatted(mocked_test_outcomes_dataset_event.run_task.start_time),
        "run_expected_start_time": None,
        "run_expected_end_time": None,
        "run_name": None,
        "run_key": None,
        "rule_consecutive_run_count": None,
        "rule_group_by_run_name": None,
        "rule_only_exact_count": None,
        "rule_run_state_matches": None,
    }
    actual_data_points = action._get_data_points(mocked_test_outcomes_dataset_event, rule_mock, uuid4())
    assert actual_data_points == expected_data_points


@pytest.mark.unit
def test_journey_and_task_names_missing(action, mocked_test_outcomes_dataset_event, rule_mock, project_service):
    email_to = "success@example.com"
    email_from = "test@domain.com"
    template_name = "TestTemplateNested"
    action = SendEmailAction(action, {"from_address": email_from, "recipients": [email_to], "template": template_name})
    project_service.return_value = Page(results=[], total=0)
    type(mocked_test_outcomes_dataset_event.task).display_name = PropertyMock(side_effect=DoesNotExist)
    with patch("rules_engine.actions.send_email_action.Journey.get_by_id", side_effect=DoesNotExist):
        expected_data_points = {
            **mocked_test_outcomes_dataset_event.as_dict(),
            "journey_name": "N/A",
            "component_name": mocked_test_outcomes_dataset_event.component.display_name,
            "component_key": mocked_test_outcomes_dataset_event.dataset_key,
            "task_name": "",
            "base_url": "",
            "project_name": mocked_test_outcomes_dataset_event.project.name,
            "event_timestamp_formatted": datetime_formatted(mocked_test_outcomes_dataset_event.event_timestamp),
            "run_task_start_time": datetime_formatted(mocked_test_outcomes_dataset_event.run_task.start_time),
            "run_expected_start_time": None,
            "run_expected_end_time": None,
            "run_name": None,
            "run_key": None,
            "rule_consecutive_run_count": None,
            "rule_group_by_run_name": None,
            "rule_only_exact_count": None,
            "rule_run_state_matches": None,
        }
        actual_data_points = action._get_data_points(mocked_test_outcomes_dataset_event, rule_mock, uuid4())
        assert actual_data_points == expected_data_points
