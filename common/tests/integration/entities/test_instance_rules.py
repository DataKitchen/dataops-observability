import uuid

import pytest
from peewee import IntegrityError

from common.entities import InstanceRule


@pytest.mark.integration
@pytest.mark.parametrize(
    "invalid_rule",
    [
        {},
        {"batch_pipeline_id": None},
        {"expression": None},
        {"batch_pipeline_id": None, "expression": None},
    ],
)
def test_instance_rule_check_none(invalid_rule, journey, action):
    """IntegrityError raised when creating an InstanceRule without a component or schedule."""
    with pytest.raises(IntegrityError, match="component_xor_schedule"):
        data = {"journey": journey, "action": action}
        InstanceRule.create(**data, **invalid_rule)


@pytest.mark.integration
def test_instance_rule_check_both_set(journey, action):
    """IntegrityError raised when creating an InstanceRule with batch-pipeline and schedule set at the same time."""
    with pytest.raises(IntegrityError, match="component_xor_schedule"):
        data = {"journey": journey, "action": action, "batch_pipeline_id": str(uuid.uuid4()), "expression": "* * * * *"}
        InstanceRule.create(**data)


@pytest.mark.integration
def test_instance_rule_check_fk_constraint(journey, action):
    """IntegrityError raised when creating an InstanceRule with non-existed batch-pipeline."""
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        InstanceRule.create(journey=journey, action=action, batch_pipeline_id=uuid.uuid4())


@pytest.mark.integration
def test_instance_rule_check_start_only(journey, action, pipeline):
    """IntegrityError raised when creating an InstanceRule without a start or end component."""
    result = InstanceRule.create(journey=journey, action=action, batch_pipeline=pipeline)
    assert InstanceRule.select().where(InstanceRule.id == result.id).exists()


@pytest.mark.integration
def test_instance_rule_check_journey_reverse(journey, action, pipeline):
    InstanceRule.create(journey=journey, action=action, batch_pipeline=pipeline)
    InstanceRule.create(journey=journey, action=action, batch_pipeline=pipeline)
    assert journey.instance_rules.count() == 2
