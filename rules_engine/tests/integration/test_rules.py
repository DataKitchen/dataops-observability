import uuid
from unittest.mock import patch

import pytest

from common.entities import Rule as RuleEntity
from common.entities import RunStatus
from common.events.v1 import TestStatuses
from rules_engine.rules import get_rules


@pytest.fixture
def action_factory_mock():
    with patch("rules_engine.rules.action_factory") as action_factory:
        yield action_factory


@pytest.mark.integration
def test_get_rules_journey_does_not_exist(test_db):
    rules = get_rules(uuid.uuid4())
    assert rules == []


@pytest.mark.integration
def test_get_rules_returned_actions(
    company, journey, pipeline, action, fake_action_class, run_status_event, action_factory_mock, journey_dag
):
    rule_entities = []
    for i in range(2):
        rule_entities.append(
            RuleEntity.create(
                action=action.action_impl,
                action_args={"idx": i},
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
        )
    assert 2 == RuleEntity.select().count()

    rules = get_rules(rule_entities[0].journey.id)
    assert 2 == len(rules)
    for rule in rules:
        rule.triggers[0](run_status_event, rule.rule_entity, rule_entities[0].journey.id)
    factory_calls = action_factory_mock.call_args_list
    assert 2 == len(factory_calls)
    assert factory_calls[0].args[0] == "CALL_WEBHOOK"
    # Comparing all action args from action_factory calls to make sure that the same rule entity was not used twice
    # (hint: there was a bug where this happened)
    assert factory_calls[0].args[1] != factory_calls[1].args[1]


@pytest.mark.integration
@pytest.mark.parametrize("component_fixture", ["dataset", "server", "stream"])
def test_non_batch_pipeline_component_get_rules(component_fixture, request, journey_2, action):
    component = request.getfixturevalue(component_fixture)
    rule_entity = RuleEntity.create(
        action=action.action_impl,
        component=component,
        journey=journey_2,
        rule_schema="simple_v1",
        rule_data={
            "when": "all",
            "conditions": [
                {"test_status": {"matches": TestStatuses.PASSED.name}},
            ],
        },
    )
    assert 1 == RuleEntity.select().count()

    rules = get_rules(rule_entity.journey.id)
    assert 1 == len(rules)
    assert rules[0].component_id == component.id
