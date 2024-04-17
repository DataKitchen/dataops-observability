import pytest

from common.entities import Rule


@pytest.mark.integration
def test_rule_create(action, pipeline, journey):
    Rule.create(
        name="test rule",
        journey=journey,
        rule_schema="fake schema",
        rule_data="fake data",
        action=action,
        component=pipeline,
    )


@pytest.mark.integration
def test_rule_defaults(action, journey):
    rule = Rule.create(
        name="test rule", rule_schema="fake schema", rule_data="fake data", action=action, journey=journey
    )
    assert rule.action_args == {}
