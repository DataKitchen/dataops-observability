from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from common.entities import Action
from common.events.v1 import ApiRunStatus, RunStatusEvent, TestOutcomesEvent, TestStatuses
from observability_api.schemas import WebhookActionArgsSchema
from rules_engine.actions.webhook_action import WebhookAction


@pytest.fixture
def session():
    with patch("rules_engine.actions.webhook_action.get_session", new=Mock()) as session:
        session.return_value = Mock()
        yield session.return_value


@pytest.fixture
def test_outcome_item_data():
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "name": "My_test_name",
        "status": TestStatuses.PASSED.name,
        "description": "My description",
        "start_time": timestamp,
        "end_time": timestamp,
        "metadata": {"some meta": "data"},
        "metric_value": 12,
        "min_threshold": 25.5,
        "max_threshold": 38,
    }


@pytest.fixture
def test_outcomes_data(test_outcome_item_data):
    test_outcome_data = {
        "pipeline_key": "Foo",
        "run_key": "Foo",
        "task_key": "Foo",
        "test_outcomes": [test_outcome_item_data, test_outcome_item_data],
    }
    return test_outcome_data


@pytest.mark.unit
def test_webhook_action_format_data(session, run, rule):
    event = RunStatusEvent.as_event_from_request(
        {"status": ApiRunStatus.RUNNING.name, "pipeline_key": "asdf", "run_key": "qwer"}
    )
    event.run_id = run.id
    action_args = {
        "url": "http://example.com?status={run.status}",
        "method": "POST",
        "payload": {
            "task_status": "status: {run.status}",
            "static1": "static text",
            "static2": 234,
            "list": ["status: {run.status}", {"listdict": "status: {run.status}"}],
            "dict": {"subkey": "status: {run.status}"},
        },
        "headers": [{"key": "one header", "value": "{run.status}"}, {"key": "two header", "value": "value2"}],
    }
    WebhookActionArgsSchema().load(action_args)
    action = WebhookAction(Action(), action_args)
    assert action.execute(event, rule, None)
    # In agreement with POs the status used should be on the entity, not the event
    session.request.assert_called_once_with(
        action_args["method"],
        f"http://example.com?status={run.status}",
        headers={"one header": f"{run.status}", "two header": "value2"},
        json={
            "task_status": f"status: {run.status}",
            "static1": "static text",
            "static2": 234,
            "list": [f"status: {run.status}", {"listdict": f"status: {run.status}"}],
            "dict": {"subkey": f"status: {run.status}"},
        },
    )


@pytest.mark.unit
def test_webhook_action_format_with_invalid_attribute(session, test_outcomes_data, rule):
    event = TestOutcomesEvent.as_event_from_request(test_outcomes_data)
    action_args = {
        "url": "a url {invaliddatapoint}",
        "method": "ye method",
        "payload": {
            "test_status": "{event.test_outcomes[0].status}",
        },
        "headers": [],
    }
    action = WebhookAction(Action(), action_args)
    assert action.execute(event, rule, None)
    session.request.assert_called_once_with(
        action_args["method"],
        action_args["url"],
        headers=None,
        json=action_args["payload"],
    )


@pytest.mark.unit
@pytest.mark.parametrize("del_attr", ("url", "method"))
def test_webhook_action_missing_args(del_attr):
    action_args = {
        "url": "a url",
        "method": "a method",
    }
    del action_args[del_attr]
    with pytest.raises(ValueError):
        WebhookAction(Action(), action_args)


@pytest.mark.unit
def test_webhook_action_default_fields(session, test_outcomes_data, rule):
    event = TestOutcomesEvent.as_event_from_request(test_outcomes_data)
    action_args = {
        "url": "a url",
        "method": "ye method",
    }
    action = WebhookAction(Action(), action_args)
    assert action.execute(event, rule, None)
    session.request.assert_called_once_with(
        action_args["method"],
        action_args["url"],
        headers=None,
        json=None,
    )
