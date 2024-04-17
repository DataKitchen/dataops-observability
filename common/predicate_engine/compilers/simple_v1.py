import logging
import re
from functools import reduce
from operator import and_, or_
from typing import Any, Union

from common.entities import AlertLevel, InstanceAlertType, RunAlert, RunAlertType, RunState
from common.predicate_engine._operators import OPERAND_MAP
from common.predicate_engine.compilers.utils import limit_query, prefetch_query
from common.predicate_engine.exceptions import InvalidRuleData
from common.predicate_engine.query import ANY, ATLEAST, EXACT_N, R

LOG = logging.getLogger(__name__)
SENTINEL_NONE = object()


def _compile_instance_alert_condition(value: dict[str, list]) -> R:
    _level_list = value["level_matches"]
    if not isinstance(_level_list, list):
        raise InvalidRuleData("`level_matches` must be an empty list or list of alert levels.")
    try:
        level_list = [getattr(AlertLevel, x) for x in _level_list]
    except AttributeError:
        raise InvalidRuleData("Not all `level_matches` values could not be coerced to an AlertLevel enum.")

    _type_list = value["type_matches"]
    if not isinstance(value["type_matches"], list):
        raise InvalidRuleData("`type_matches` must be an empty list or list of instance alert types.")
    try:
        type_list = [getattr(InstanceAlertType, x) for x in _type_list]
    except AttributeError:
        raise InvalidRuleData("Not all `type_matches` values could not be coerced to an InstanceAlertType enum.")

    r_level = R(event__level__in=level_list) if value["level_matches"] else R()
    r_type = R(event__type__in=type_list) if value["type_matches"] else R()
    if r_level or r_type:
        return r_level & r_type
    else:
        raise InvalidRuleData("At least one condition must be set.")


def _compile_task_status_condition(value: dict[str, str]) -> R:
    return R(event__status__exact=value["matches"])


def _compile_run_state_condition(value: dict) -> R:
    run_state = value["matches"]
    if run_state is RunState.RUNNING and (value["count"] != 1 or value["trigger_successive"] is not True):
        raise InvalidRuleData(
            f"Run state {value['matches']} requires default values for 'count', or 'trigger_successive'"
        )

    if run_state in (
        RunState.RUNNING,
        RunState.COMPLETED,
        RunState.COMPLETED_WITH_WARNINGS,
        RunState.FAILED,
    ):
        r = R(event__status__exact=run_state.name) & R(event__run_key__isnull=False) & R(event__task_key__isnull=True)
        runs_attr = "database__runs_filter_name__exact" if value["group_run_name"] else "database__runs__exact"

        if value["trigger_successive"] is False:
            r = r & R(
                **{
                    runs_attr: EXACT_N(
                        run_state.name,
                        attr_name="status",
                        n=value["count"],
                        transform_funcs=[limit_query(value["count"] + 1)],
                    )
                }
            )
        elif (count := value["count"]) > 1:
            r = r & R(
                **{
                    runs_attr: ATLEAST(
                        run_state.name,
                        attr_name="status",
                        n=count,
                        transform_funcs=[limit_query(value["count"])],
                    )
                }
            )
    elif run_state in (
        RunState.LATE_END,
        RunState.LATE_START,
        RunState.MISSING_RUN,
        RunState.UNEXPECTED_STATUS_CHANGE,
    ):
        alert_type = RunAlertType[run_state.name]
        r = R(event__type__exact=alert_type)
        runs_attr = "database__runs_filter_name__r" if value["group_run_name"] else "database__runs__r"
        if value["trigger_successive"] is False:
            any_matching_alert = ANY(alert_type, attr_name="type")
            r = r & R(
                **{
                    runs_attr: EXACT_N(
                        R(run_alerts__exact=any_matching_alert),
                        n=value["count"],
                        transform_funcs=[limit_query(value["count"] + 1), prefetch_query(RunAlert)],
                    )
                }
            )
        elif (count := value["count"]) > 1:
            any_matching_alert = ANY(alert_type, attr_name="type")
            r = r & R(
                **{
                    runs_attr: ATLEAST(
                        R(run_alerts__exact=any_matching_alert),
                        n=value["count"],
                        transform_funcs=[limit_query(limit=value["count"]), prefetch_query(RunAlert)],
                    )
                }
            )
    else:
        raise InvalidRuleData("Invalid run state value {value['matches']}")
    return r


def _compile_test_status_condition(value: dict[str, str]) -> R:
    return R(event__test_outcomes__exact=ANY(value["matches"], attr_name="status"))


def _compile_metric_log_condition(value: dict[str, Any]) -> R:
    if (op := value.get("operator", "").lower()) not in OPERAND_MAP:
        raise InvalidRuleData(f"Operator `{op}` not one of allowed: {', '.join(OPERAND_MAP.keys())}")
    if (field_name := value.get("key", None)) is None:
        raise InvalidRuleData(f"Key `{field_name}` cannot be a null value.")
    if (match_value := value.get("static_value", SENTINEL_NONE)) is SENTINEL_NONE:
        raise InvalidRuleData("The `static_value` key must be present.")
    return R(**{"event__metric_key__exact": field_name, f"event__metric_value__{op}": match_value})


def _compile_message_log_condition(value: dict[str, Any]) -> R:
    if (levels := value.get("level", SENTINEL_NONE)) is SENTINEL_NONE:
        raise InvalidRuleData("Message log rules require a `level` key.")
    if not isinstance(levels, list):
        raise InvalidRuleData("Message log `level` must be an empty list or list of log levels")
    if levels:
        base_rule = reduce(or_, [R(event__log_level__exact=level) for level in levels])
    else:
        base_rule = R(event__log_level__isnull=False)

    regex = value.get("matches", None)
    if regex:
        try:
            re.compile(regex)
        except Exception as e:
            raise InvalidRuleData(f"Message log `matches` value: `{regex}` is not a valid regular expression") from e
        base_rule &= R(event__message__regex=regex)
    return base_rule


STATIC_RULES = {
    "message_log": R(event__message__isnull=False),
    "metric_log": R(event__metric_value__isnull=False),
    "task_status": R(event__task_key__isnull=False),
}
"""A map of base queries to be AND'd to the compiled result depending on rule type."""


CONDITION_COMPILERS = {
    "instance_alert": _compile_instance_alert_condition,
    "message_log": _compile_message_log_condition,
    "metric_log": _compile_metric_log_condition,
    "run_state": _compile_run_state_condition,
    "task_status": _compile_task_status_condition,
    "test_status": _compile_test_status_condition,
}
"""A map of rule compilers specific to a particular rule type."""


def compile_simple_v1_schema(rule_data: dict[str, Union[str, list[dict[str, dict[str, str]]]]]) -> R:
    # Determine the joining rule; defaults to AND, but is OR if when is set to "any"
    when = rule_data.get("when", "all")
    if not isinstance(when, str):
        raise InvalidRuleData(f"Expected `when` to be a string value, got {type(when)}")

    if when not in ("any", "all"):
        raise InvalidRuleData(f"Invalid `when` value. Must be `any` or `all`, got {when}")

    op = {"any": or_, "all": and_}.get(when, and_)

    # Validate conditions list
    conditions = rule_data.get("conditions")
    if not conditions:
        raise InvalidRuleData("No conditions were provided.")
    if not isinstance(conditions, list):
        raise InvalidRuleData(f"Conditions must be a list, got {type(conditions)}.")
    parts = []
    rule_names = set()
    invalid_names = set()
    for condition in conditions:
        if not isinstance(condition, dict):
            raise InvalidRuleData("Condition should be a mapping in the form of {field.name: {'matches': value}}")
        for key, value in condition.items():
            if (comp_func := CONDITION_COMPILERS.get(key, None)) is not None:
                try:
                    parts.append(comp_func(value))
                except Exception as e:
                    raise InvalidRuleData(f"Unable to compile `{key}` condition") from e
                rule_names.add(key)
            else:
                invalid_names.add(key)

    if invalid_names:
        raise InvalidRuleData(
            f"simple_v1 schema received one ore more unsupported rule types: `{', '.join(invalid_names)}`"
        )

    if len(rule_names) > 1:
        raise InvalidRuleData(f"simple_v1 schema only supports matching on a rule type. Got: `{', '.join(rule_names)}`")
    if len(rule_names) == 0:
        raise InvalidRuleData("simple_v1 schema requires at least one rule type. No valid rule type was found.")
    rule_obj = reduce(op, parts)
    rule_type = rule_names.pop()
    if rule_type in STATIC_RULES:
        rule_obj &= STATIC_RULES[rule_type]

    return rule_obj
