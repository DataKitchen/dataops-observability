from datetime import datetime, timedelta

import pytest

from common.entities import AlertLevel, Run, RunAlert, RunAlertType, RunState, RunStatus
from common.predicate_engine.compilers import compile_simple_v1_schema
from common.predicate_engine.exceptions import InvalidRuleData
from common.predicate_engine.schemas.simple_v1 import RuleDataSchema
from rules_engine.rule_data import RuleData
from testlib.fixtures.entities import *
from testlib.fixtures.v1_events import *
from testlib.fixtures.v2_events import run_alert  # noqa: F401


@pytest.fixture
def runs(pipeline):
    return [
        Run.create(start_time=datetime.utcnow(), status=RunStatus.COMPLETED.name, key="k1", pipeline=pipeline),
        Run.create(
            start_time=datetime.utcnow() - timedelta(hours=1),
            status=RunStatus.COMPLETED.name,
            key="k2",
            pipeline=pipeline,
        ),
    ]


@pytest.fixture
def runs_w_alerts(runs):
    for run in runs:
        RunAlert.create(type=RunAlertType.MISSING_RUN, level=AlertLevel.ERROR, description="", run=run)
        RunAlert.create(type=RunAlertType.LATE_START, level=AlertLevel.WARNING, description="", run=run)
    return runs


@pytest.fixture
def base_rule_pattern():
    return {
        "when": "all",
        "conditions": [{}],
    }


@pytest.mark.integration
@pytest.mark.parametrize(
    "condition",
    (
        {"matches": "invalid value"},
        {"matches": RunState.RUNNING, "count": 2, "trigger_successive": True, "group_run_name": False},
    ),
)
def test_run_state_invalid_state(condition, base_rule_pattern):
    base_rule_pattern["conditions"][0]["run_state"] = condition

    with pytest.raises(InvalidRuleData, match="run_state"):
        compile_simple_v1_schema(base_rule_pattern)


@pytest.mark.integration
def test_run_state_match_single_run_status(pipeline, base_rule_pattern, COMPLETED_run_status_event, run_alert):
    COMPLETED_run_status_event.pipeline_id = pipeline.id
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.COMPLETED.name,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is True
    assert rule.matches(RuleData(run_alert)) is False


@pytest.mark.integration
def test_run_state_match_exact_single_run_status(pipeline, runs, base_rule_pattern, FAILED_run_status_event, run_alert):
    FAILED_run_status_event.pipeline_id = pipeline.id
    runs[0].status = RunStatus.FAILED.name
    runs[0].save()
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.FAILED.name,
        "trigger_successive": False,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(FAILED_run_status_event)) is True
    assert rule.matches(RuleData(run_alert)) is False

    base_rule_pattern["conditions"][0]["run_state"]["count"] = 2
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(FAILED_run_status_event)) is False


@pytest.mark.integration
def test_run_state_match_exact_two_run_status(pipeline, runs, base_rule_pattern, COMPLETED_run_status_event, run_alert):
    COMPLETED_run_status_event.pipeline_id = pipeline.id
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.COMPLETED.name,
        "count": 2,
        "trigger_successive": False,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is True
    assert rule.matches(RuleData(run_alert)) is False

    base_rule_pattern["conditions"][0]["run_state"]["count"] = 1
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is False


@pytest.mark.integration
def test_run_state_match_two_run_status(pipeline, runs, base_rule_pattern, COMPLETED_run_status_event, run_alert):
    COMPLETED_run_status_event.pipeline_id = pipeline.id
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.COMPLETED.name,
        "count": 2,
        "trigger_successive": True,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is True
    assert rule.matches(RuleData(run_alert)) is False

    base_rule_pattern["conditions"][0]["run_state"]["count"] = 3
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is False


@pytest.mark.integration
def test_run_state_match_exact_single_run_status_grouped(
    pipeline, runs, base_rule_pattern, COMPLETED_run_status_event, run_alert
):
    COMPLETED_run_status_event.pipeline_id = pipeline.id
    COMPLETED_run_status_event.run_id = runs[0].id
    runs[0].name = "test name"
    runs[0].save()
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.COMPLETED.name,
        "count": 1,
        "trigger_successive": False,
        "group_run_name": True,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is True
    assert rule.matches(RuleData(run_alert)) is False

    runs[1].name = runs[0].name
    runs[1].save()
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is False


@pytest.mark.integration
def test_run_state_match_two_run_status_grouped(
    pipeline, runs, base_rule_pattern, COMPLETED_run_status_event, run_alert
):
    COMPLETED_run_status_event.pipeline_id = pipeline.id
    COMPLETED_run_status_event.run_id = runs[0].id
    for run in runs:
        run.name = "test name"
        run.save()
    run3 = Run.create(start_time=datetime.utcnow(), status=RunStatus.COMPLETED.name, key="k3", pipeline=pipeline)
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.COMPLETED.name,
        "count": 2,
        "trigger_successive": False,
        "group_run_name": True,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is True
    assert rule.matches(RuleData(run_alert)) is False

    run3.name = runs[0].name
    run3.save()
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is False


@pytest.mark.integration
def test_run_state_match_single_run_alert(base_rule_pattern, COMPLETED_run_status_event, run_alert):
    run_alert.type = RunAlertType.LATE_END
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.LATE_END.name,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is False
    assert rule.matches(RuleData(run_alert)) is True


@pytest.mark.integration
def test_run_state_match_exact_run_alert(
    pipeline, runs_w_alerts, base_rule_pattern, COMPLETED_run_status_event, run_alert
):
    run_alert.type = RunAlertType.MISSING_RUN
    run_alert.batch_pipeline_id = pipeline.id
    run_alert.run_id = runs_w_alerts[0].id
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.MISSING_RUN.name,
        "trigger_successive": False,
        "count": 2,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is False
    assert rule.matches(RuleData(run_alert)) is True

    base_rule_pattern["conditions"][0]["run_state"]["count"] = 1
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(run_alert)) is False

    runs_w_alerts[0].name = "test name"
    runs_w_alerts[0].save()
    base_rule_pattern["conditions"][0]["run_state"]["group_run_name"] = True
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(run_alert)) is True

    base_rule_pattern["conditions"][0]["run_state"]["matches"] = RunState.LATE_END.name
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(run_alert)) is False


@pytest.mark.integration
def test_run_state_match_successive_run_alert(
    pipeline, runs_w_alerts, base_rule_pattern, COMPLETED_run_status_event, run_alert
):
    run3 = Run.create(start_time=datetime.utcnow(), status=RunStatus.COMPLETED.name, key="k3", pipeline=pipeline)
    RunAlert.create(type=RunAlertType.LATE_START, level=AlertLevel.ERROR, description="", run=run3)

    run_alert.type = RunAlertType.LATE_START
    run_alert.batch_pipeline_id = pipeline.id
    run_alert.run_id = runs_w_alerts[0].id
    base_rule_pattern["conditions"][0]["run_state"] = {
        "matches": RunState.LATE_START.name,
        "trigger_successive": True,
        "count": 2,
    }

    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(COMPLETED_run_status_event)) is False
    assert rule.matches(RuleData(run_alert)) is True

    base_rule_pattern["conditions"][0]["run_state"]["count"] = 4
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(run_alert)) is False

    for i in range(2):
        runs_w_alerts[i].name = "test name"
        runs_w_alerts[i].save()
    base_rule_pattern["conditions"][0]["run_state"]["count"] = 2
    base_rule_pattern["conditions"][0]["run_state"]["group_run_name"] = True
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(run_alert)) is True

    base_rule_pattern["conditions"][0]["run_state"]["count"] = 3
    rule = compile_simple_v1_schema(RuleDataSchema().load(base_rule_pattern))
    assert rule.matches(RuleData(run_alert)) is False
