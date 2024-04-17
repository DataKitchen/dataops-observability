import pytest

from observability_api.schemas import InstanceRuleSchema
from testlib.fixtures.entities import *


@pytest.mark.unit
def test_instance_rule_schema_dump_schedule(journey, instance_rule_start):
    data = InstanceRuleSchema().dump(instance_rule_start)
    assert data["journey"] == str(instance_rule_start.journey.id)
    assert data["schedule"] == {"expression": instance_rule_start.expression, "timezone": instance_rule_start.timezone}
    assert all(k not in ["expression", "timezone"] for k in data.keys())


@pytest.mark.unit
def test_instance_rule_schema_dump_default_schedule(journey, instance_rule_pipeline_start):
    data = InstanceRuleSchema().dump(instance_rule_pipeline_start)
    assert data["journey"] == str(instance_rule_pipeline_start.journey.id)
    assert data["batch_pipeline"] == str(instance_rule_pipeline_start.batch_pipeline.id)
    assert data["schedule"] is None
    assert all(k not in ["expression", "timezone"] for k in data.keys())
