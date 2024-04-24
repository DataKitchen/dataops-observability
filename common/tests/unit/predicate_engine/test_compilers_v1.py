from decimal import Decimal

import pytest

from common.entities import AlertLevel, InstanceAlertType, RunState
from common.predicate_engine.compilers import compile_simple_v1_schema
from common.predicate_engine.exceptions import InvalidRuleData
from common.predicate_engine.query import ANY, R
from rules_engine.rule_data import RuleData

from .assertions import assertRuleEqual


@pytest.mark.unit
@pytest.mark.parametrize(
    "condition,expected",
    [
        (
            {"when": "all", "conditions": [{"test_status": {"matches": "PASSED"}}]},
            R(event__test_outcomes__exact=ANY("PASSED", attr_name="status")),
        ),
        (
            {"when": "all", "conditions": [{"task_status": {"matches": "FAILED"}}]},
            R(event__status__exact="FAILED") & R(event__task_key__isnull=False),
        ),
        (
            {"when": "all", "conditions": [{"task_status": {"matches": "COMPLETED_WITH_WARNINGS"}}]},
            R(event__status__exact="COMPLETED_WITH_WARNINGS") & R(event__task_key__isnull=False),
        ),
        (
            {
                "when": "all",
                "conditions": [
                    {"metric_log": {"key": "metric_key", "operator": "exact", "static_value": Decimal("100")}}
                ],
            },
            R(event__metric_key__exact="metric_key")
            & R(event__metric_value__isnull=False)
            & R(event__metric_value__exact=Decimal("100")),
        ),
        (
            {
                "when": "all",
                "conditions": [
                    {"metric_log": {"key": "metric_other_key", "operator": "gte", "static_value": Decimal("345.0")}}
                ],
            },
            R(event__metric_key__exact="metric_other_key")
            & R(event__metric_value__isnull=False)
            & R(event__metric_value__gte=Decimal("345.0")),
        ),
        (
            {"when": "all", "conditions": [{"message_log": {"level": ["DEBUG"]}}]},
            R(event__log_level__exact="DEBUG") & R(event__message__isnull=False),
        ),
        (
            {"when": "all", "conditions": [{"message_log": {"level": ["DEBUG", "INFO"]}}]},
            (R(event__log_level__exact="DEBUG") | R(event__log_level__exact="INFO")) & R(event__message__isnull=False),
        ),
        (
            {"when": "all", "conditions": [{"message_log": {"level": []}}]},
            R(event__log_level__isnull=False) & R(event__message__isnull=False),
        ),
        (
            {"when": "all", "conditions": [{"message_log": {"level": ["DEBUG"], "matches": ".+?[.]py"}}]},
            R(event__log_level__exact="DEBUG") & R(event__message__regex=".+?[.]py") & R(event__message__isnull=False),
        ),
        (
            {
                "when": "all",
                "conditions": [{"instance_alert": {"level_matches": ["WARNING"], "type_matches": ["LATE_START"]}}],
            },
            R(event__level__in=[AlertLevel.WARNING]) & R(event__type__in=[InstanceAlertType.LATE_START]),
        ),
        (
            {"when": "all", "conditions": [{"instance_alert": {"level_matches": ["WARNING"], "type_matches": []}}]},
            R(event__level__in=[AlertLevel.WARNING]),
        ),
    ],
)
def test_data_to_rule(condition, expected):
    actual = compile_simple_v1_schema(condition)
    assertRuleEqual(expected, actual, default_op="exact")


@pytest.mark.unit
@pytest.mark.parametrize(
    "condition,search,value",
    [
        (
            {"when": "all", "conditions": [{"task_status": {"matches": "COMPLETED_WITH_WARNINGS"}}]},
            R(event__status__exact="COMPLETED_WITH_WARNINGS") & R(event__task_key__isnull=False),
            False,
        ),
    ],
)
def test_compare_match(condition, search, value, simple_entity):
    actual = compile_simple_v1_schema(condition).matches(RuleData(simple_entity))
    expected = search.matches(RuleData(simple_entity))
    assert expected is value, f"Search {search} should have yielded {value}"
    assert expected is actual, f"Condition {condition} should have yielded {expected}"
    assert value is actual, f"Condition {condition} should have yielded {value}"


@pytest.mark.unit
@pytest.mark.parametrize(
    "condition",
    [
        {"when": "all", "values": [{"task": {"matches": "COMPLETED_WITH_WARNINGS"}}]},
        {"when": "all", "conditions": [{"message_log": {"level": [], "matches": "[.*"}}]},  # Invalid regex
        {
            "when": "all",
            "conditions": [
                {"task_status": {"matches": "COMPLETED_WITH_WARNINGS"}},
                {"run_state": {"matches": RunState.LATE_END.name}},
            ],
        },  # There cannot be two field types in conditions
        {"when": None},  # `when` must be a string
        {"when": "all", "conditions": [{"status": {"matches": "COMPLETED_WITH_WARNINGS"}}]},
        {"when": "none", "values": [{"total_things": {"attributes": 1}}]},
        {"when": "all", "conditions": [{"val": {"match": "FAILED"}}]},  # Key should be `matches`
        {"when": "all"},  # Condition missing entirely
        {"when": "all", "conditions": None},  # Conditions has to be a list
        {"when": "all", "conditions": []},  # Conditions have to be provided
        {"when": "all", "conditions": [{"val": None}]},  # Value must have a matches dict
        {
            "when": "all",  # Operator not one of allowed values
            "conditions": [{"metric_log": {"key": "task_key", "operator": "badoperator", "static_value": "foo"}}],
        },
        {"when": "all", "conditions": [{"metric_log": {"static_value": "a", "operator": "in"}}]},  # No `key`
        {"when": "all", "conditions": [{"metric_log": {"key": "task_key", "operator": "iexact"}}]},  # No `static_value`
        {"when": "all", "conditions": [{"message_log": {"level": "DEBUG"}}]},  # `level` should be a list
        {"when": "all", "conditions": [{"message_log": {"matches": ".+?[.]py"}}]},  # `level` is missing
        {"when": "all", "conditions": [{}]},  # `Rule type is missing completely`
        {
            "when": "all",
            "conditions": [{"level_matches": [], "type_matches": []}],
        },  # Alert levels and types conditions are both missing
        {"when": "all", "conditions": [{"level_matches": []}]},
        {"when": "all", "conditions": [{"type_matches": []}]},
        {"when": "all", "conditions": [{"level_matches": "not a list"}]},
        {"when": "all", "conditions": [{"type_matches": {"msg": "not a list"}}]},
        {"when": "all", "conditions": [{"instance_alert": {"level_matches": ["BADLEVEL"], "type_matches": []}}]},
        {
            "when": "all",
            "conditions": [{"instance_alert": {"level_matches": ["WARNING"], "type_matches": ["BADTYPE"]}}],
        },
        {"when": "all", "conditions": [{"instance_alert": {"level_matches": ["WARNING"], "type_matches": "NOTLIST"}}]},
        {
            "when": "all",
            "conditions": [{"instance_alert": {"level_matches": "NOT_LIST", "type_matches": ["LATE_START"]}}],
        },
    ],
)
def test_bad_rule(condition):
    """Bad rule data raises InvalidRuleData exception."""
    with pytest.raises(InvalidRuleData):
        compile_simple_v1_schema(condition)
