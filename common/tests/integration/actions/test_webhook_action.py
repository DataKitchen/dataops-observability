import pytest

from common.entities import DB, Action, Company, Organization, Pipeline, Project, Run, ActionImpl, RunStatus, Rule
from common.events.v1 import ApiRunStatus, RunStatusEvent
from conf import init_db
from common.schemas.action_schemas import HttpMethod, WebhookActionArgsSchema
from common.actions.webhook_action import WebhookAction
from rules_engine.journey_rules import _get_rules
from testlib.fixtures.web_server import webhook_server  # noqa: F401


@pytest.fixture
def database():
    init_db()
    yield
    DB.close()


@pytest.fixture
def run(database):
    company = Company.create(name="Foo")
    org = Organization.create(name="Foo", company=company)
    proj = Project.create(name="Foo", active=True, organization=org)
    pipeline = Pipeline.create(key="Foo", project=proj)
    return Run.create(key="test key", status="SOME STATUS", pipeline=pipeline)


@pytest.fixture
def action(company):
    action = Action.create(name="action1", company=company, action_impl=ActionImpl.CALL_WEBHOOK.value)
    yield action


@pytest.fixture
def db_rule(journey, pipeline, action):
    _get_rules.cache_clear()
    rule = Rule.create(
        action=action.action_impl,
        component=pipeline,
        journey=journey,
        rule_schema="simple_v1",
        rule_data={
            "when": "all",
            "conditions": [
                {"task_status": {"matches": RunStatus.RUNNING.name}},
            ],
        },
    )
    yield rule


@pytest.mark.integration
def test_webhook_action_success(webhook_server, run, journey, db_rule):
    db_rule.action_args = {
        "url": f"http://127.0.0.1:{webhook_server.listening_port}/testhook?key={{pipeline.key}}",
        "method": HttpMethod.POST.name,
        "payload": {
            "task_status": "status: {run.status}",
            "component_type": "type: {component.type}",
        },
        "headers": [{"key": "Content-Type", "value": "application/json"}],
    }
    WebhookActionArgsSchema().load(db_rule.action_args)
    webhook_action = WebhookAction(Action(), db_rule.action_args)
    event = RunStatusEvent.as_event_from_request(
        {"status": ApiRunStatus.FAILED.name, "pipeline_key": "asdf", "run_key": "qwer"}
    )
    event.run_id = run.id
    event.component_id = run.pipeline_id

    action_result = webhook_action.execute(event, db_rule, journey.id)
    assert action_result
    assert len(webhook_server.received_data) == 1
    assert webhook_server.received_data[0].payload == {
        "task_status": f"status: {run.status}",
        "component_type": "type: BATCH_PIPELINE",
    }
    assert webhook_server.received_data[0].args["key"] == event.pipeline_key


@pytest.mark.integration
def test_webhook_action_invalid_method(webhook_server, journey, db_rule):
    db_rule.action_args = {
        "url": f"http://127.0.0.1:{webhook_server.listening_port}/testhook",
        "method": HttpMethod.GET.name,
    }
    webhook_action = WebhookAction(Action(), db_rule.action_args)
    event = RunStatusEvent.as_event_from_request(
        {"status": ApiRunStatus.FAILED.name, "pipeline_key": "asdf", "run_key": "qwer"}
    )

    action_result = webhook_action.execute(event, db_rule, journey.id)
    assert not action_result
    assert len(webhook_server.received_data) == 0


@pytest.mark.integration
def test_webhook_action_invalid_endpoint(webhook_server, journey, db_rule):
    action_args = {
        "url": f"http://127.0.0.1:{webhook_server.listening_port}/invalidendpoint",
        "method": HttpMethod.POST.name,
    }
    webhook_action = WebhookAction(Action(), action_args)
    event = RunStatusEvent.as_event_from_request(
        {"status": ApiRunStatus.FAILED.name, "pipeline_key": "asdf", "run_key": "qwer"}
    )

    action_result = webhook_action.execute(event, db_rule, journey.id)
    assert not action_result
    assert len(webhook_server.received_data) == 0
