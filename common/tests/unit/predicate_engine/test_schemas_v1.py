import pytest
from marshmallow import ValidationError

from common.entities import RunState, RunStatus
from common.events.v1 import MessageEventLogLevel
from common.predicate_engine.schemas.simple_v1 import (
    ConditionSchema,
    RuleDataSchema,
    RunStateConditionSchema,
    RunStatusConditionSchema,
)


@pytest.fixture
def task_status_condition_data():
    return {"task_status": {"matches": RunStatus.COMPLETED_WITH_WARNINGS.name}}


@pytest.fixture
def message_log_condition_data():
    return {"message_log": {"level": ["WARNING"], "matches": r"abc[de]{2}fg"}}


@pytest.fixture
def rule_data(task_status_condition_data):
    return {"when": "any", "conditions": [task_status_condition_data]}


@pytest.mark.unit
def test_condition_task_status_when(rule_data):
    for when in ("ANY", "ALL"):
        rule_data["when"] = when
        result = RuleDataSchema().load(rule_data)
        assert result["when"] == when.lower()

    rule_data["when"] = "invalid"
    with pytest.raises(ValidationError):
        RuleDataSchema().load(rule_data)


@pytest.mark.unit
def test_condition_task_status_required():
    with pytest.raises(ValidationError) as e:
        RuleDataSchema().load({})
    assert (len(e.value.args[0])) and len(e.value.args) == 1
    for required in ("when", "conditions"):
        assert e.value.args[0][required] == ["Missing data for required field."]


@pytest.mark.unit
def test_condition_task_status_statuses():
    for e in RunStatus:
        valid_data = {"matches": e.name.lower()}
        result = RunStatusConditionSchema().load(valid_data)
        assert result["matches"] == e.name.upper()


@pytest.mark.unit
def test_condition_message_log(message_log_condition_data):
    for lvl in MessageEventLogLevel:
        message_log_condition_data["message_log"]["level"] = [lvl.name]
        loaded_data = ConditionSchema().load(message_log_condition_data)["message_log"]
        input_data = message_log_condition_data["message_log"]
        assert loaded_data["level"] == input_data["level"]
        assert loaded_data["matches"] == input_data["matches"]


@pytest.mark.unit
def test_condition_task_status_matches(task_status_condition_data):
    for trigger in RunStatus:
        task_status_condition_data["task_status"]["matches"] = trigger.name.lower()
        result = ConditionSchema().load(task_status_condition_data)
        assert result["task_status"]["matches"] == trigger.name

    task_status_condition_data["task_status"]["invalid_key"] = trigger.name.lower()
    with pytest.raises(ValidationError):
        RuleDataSchema().load(task_status_condition_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    "rule_data",
    [
        {},
        {
            "task": {"matches": RunStatus.COMPLETED_WITH_WARNINGS.name},
            "run": {"matches": RunStatus.COMPLETED_WITH_WARNINGS.name},
        },
        {
            "task_status": {"matches": RunStatus.COMPLETED_WITH_WARNINGS.name},
            "run_state": {"matches": RunState.RUNNING.name},
        },
        {"metric_log": []},
        {"message_log": []},
        {"message_log": {"matches": "foo.+?"}},
        {"message_log": {"levels": ["W"], "matches": "foo*"}},
        {"message_log": {"level": "WARNING", "matches": r"foo*"}},
        {"message_log": {"level": ["WARNING", "INVALID"], "matches": r"foo*"}},
        {"message_log": {"levels": ["WARNING"], "matches": "foo("}},
        {"metric_log": {"operator": "exact", "key": "somekey"}},
        {"invalid_key": {"operator": "exact", "key": "somekey", "static_value": "value"}},
    ],
)
def test_invalid_condition_rules(rule_data):
    with pytest.raises(ValidationError):
        ConditionSchema().load(rule_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    "in_value,expected_key",
    [
        ({"metric_log": {"operator": "exact", "key": "somekey", "static_value": "10"}}, "metric_log"),
        ({"task_status": {"matches": RunStatus.COMPLETED_WITH_WARNINGS.name}}, "task_status"),
        ({"run_state": {"matches": RunState.COMPLETED_WITH_WARNINGS.name}}, "run_state"),
        ({"message_log": {"level": []}}, "message_log"),
    ],
)
def test_conditional_metric_log_no_extra_keys_dump(in_value, expected_key):
    rule_types = set(ConditionSchema.VALID_KEYS)
    to_exclude = rule_types ^ {expected_key}
    loaded = ConditionSchema().load(in_value)
    dumped = ConditionSchema().dump(loaded)
    for exclude in to_exclude:
        assert exclude not in dumped
    assert expected_key in dumped


@pytest.mark.unit
def test_run_state_defaults():
    data = {"matches": RunState.RUNNING.name}
    result = RunStateConditionSchema().load(data)
    assert result["count"] == 1
    assert result["trigger_successive"] is True
    assert result["group_run_name"] is False


@pytest.mark.unit
@pytest.mark.parametrize(
    "valid_data",
    [
        ({"matches": RunState.LATE_START.name}),
        ({"matches": RunState.UNEXPECTED_STATUS_CHANGE.name, "count": 1}),
        ({"matches": RunState.COMPLETED.name, "count": 250}),
        ({"matches": RunState.MISSING_RUN.name, "trigger_successive": True}),
        ({"matches": RunState.FAILED.name, "group_run_name": False}),
        (
            {
                "matches": RunState.COMPLETED_WITH_WARNINGS.name,
                "count": 3,
                "trigger_successive": True,
                "group_run_name": False,
            }
        ),
    ],
)
def test_run_state_valid(valid_data):
    ConditionSchema().load({"run_state": valid_data})


@pytest.mark.unit
@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        ({"matches": "invalid state"}, "matches"),
        ({"matches": RunState.FAILED.name, "count": 0}, "count"),
        ({"matches": RunState.FAILED.name, "count": 251}, "count"),
        ({"matches": RunState.FAILED.name, "trigger_successive": "not bool"}, "trigger_successive"),
        ({"matches": RunState.FAILED.name, "group_run_name": "not bool"}, "group_run_name"),
        ({"matches": RunState.RUNNING.name, "count": 2}, "count above 1"),
        ({"matches": RunState.RUNNING.name, "trigger_successive": False}, "when trigger_successive is false"),
    ],
)
def test_run_state_invalid(invalid_data, expected_error):
    with pytest.raises(ValidationError, match=expected_error):
        ConditionSchema().load({"run_state": invalid_data})
