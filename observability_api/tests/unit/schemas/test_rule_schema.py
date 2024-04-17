from unittest.mock import patch

import pytest
from marshmallow import ValidationError

from common.entities import RunStatus
from observability_api.schemas import RulePatchSchema, RuleSchema


@pytest.fixture
def task_status_condition_data():
    return {"task_status": {"matches": RunStatus.COMPLETED_WITH_WARNINGS.name}}


@pytest.fixture
def rule_data(task_status_condition_data):
    return {"when": "any", "conditions": [task_status_condition_data]}


@pytest.fixture
def rule_schema_data(rule_data):
    return {
        "action_args": {},
        "action": "SEND_EMAIL",
        "rule_data": rule_data,
        "rule_schema": "test_schema",
    }


@pytest.fixture
def email_send_action_args():
    return {
        "recipients": ["test1@domain.com", "test2@domain.com"],
        "template": "FooTemplate",
    }


@pytest.mark.unit
def test_rule_email_action_args_decode(rule_schema_data, email_send_action_args):
    rule_schema_data["action_args"] = email_send_action_args

    # This tests that the validator correctly validates an SendEmail action_Args field.
    ex = RuleSchema().load(rule_schema_data)
    assert ex.action == rule_schema_data["action"]
    assert ex.action_args == email_send_action_args


@pytest.mark.unit
def test_rules_email_action_args_decode_false(rule_schema_data):
    email_action_args = {"template": "", "recipients": ["bar"], "from_address": "aaa", "baz": {}}
    rule_schema_data["action_args"] = email_action_args

    with pytest.raises(ValidationError) as e:
        RuleSchema().load(rule_schema_data)
    assert len(e.value.args[0]) == 4
    assert "template" in e.value.args[0]
    assert "recipients" in e.value.args[0]
    assert "from_address" in e.value.args[0]
    assert "baz" in e.value.args[0]


@pytest.mark.unit
def test_rule_patch_schema(rule_schema_data, email_send_action_args):
    rule_schema_data["action_args"] = email_send_action_args
    rule_schema_data.pop("rule_schema")
    assert RulePatchSchema().load(rule_schema_data)

    rule_schema_data["action_args"]["from_address"] = "not_an_email_address"
    with pytest.raises(ValidationError):
        RulePatchSchema().load(rule_schema_data)


@pytest.mark.unit
def test_rule_patch_schema_missing_action_or_action_args(rule_schema_data, email_send_action_args):
    rule_schema_data["action_args"] = email_send_action_args
    rule_schema_data.pop("rule_schema")
    action = rule_schema_data.pop("action")

    with pytest.raises(ValidationError) as e:
        RulePatchSchema().load(rule_schema_data)
    assert e.value.args[0].get("action") == "A change in action_args requires an identifying action."

    rule_schema_data.pop("action_args")
    rule_schema_data["action"] = action
    with pytest.raises(ValidationError) as e:
        RulePatchSchema().load(rule_schema_data)
    assert e.value.args[0].get("action_args") == "A change in action requires action_args."


@pytest.mark.unit
@pytest.mark.parametrize("schema_class", (RuleSchema, RulePatchSchema), ids=("post", "patch"))
def test_rule_data_validation(schema_class, rule_schema_data, email_send_action_args):
    rule_schema_data["action_args"] = email_send_action_args
    if schema_class is RulePatchSchema:
        rule_schema_data.pop("rule_schema")

    with patch("observability_api.schemas.rule_schemas.RuleDataSchema") as rule_data_schema_mock:
        rule_data_schema_mock.return_value.load.side_effect = ValidationError("invalid")
        rule_schema = schema_class()

        with pytest.raises(ValidationError) as e:
            rule_schema.load(rule_schema_data)

    assert "rule_data" in e.value.messages_dict, str(e)
