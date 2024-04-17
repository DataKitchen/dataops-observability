from uuid import UUID

import pytest

from observability_api.schemas import TestGenTestOutcomeIntegrationSchema, TestOutcomeItemSchema
from observability_api.schemas.testgen_test_outcome_schemas import Integration
from testlib.fixtures import entities

test_outcome = entities.test_outcome
test_outcome_integration_1 = entities.test_outcome_integration_1
test_outcome_integration_2 = entities.test_outcome_integration_2


@pytest.mark.integration
def test_test_outcome_item_dump(test_outcome):
    data = TestOutcomeItemSchema().dump(test_outcome)

    assert "test-outcome-1" == data["name"]
    assert "test-outcome-key-1" == data["key"]
    assert "2000-03-09T12:11:10+00:00" == data["start_time"]
    assert "2000-03-09T13:12:11+00:00" == data["end_time"]
    assert ["a", "b", "c"] == data["dimensions"]
    assert "test-outcome-result-1" == data["result"]
    assert "test-outcome-type-1" == data["type"]
    assert "test-outcome-key-1" == data["key"]
    assert "some-metric" == data["metric_name"]
    assert "This is a metric description" == data["metric_description"]

    try:
        UUID(data["id"])
    except Exception:
        raise AssertionError(f"ID {data['id']} is not a valid UUID")


@pytest.mark.integration
def test_test_outcome_integration_dump(test_outcome_integration_1):
    data = TestGenTestOutcomeIntegrationSchema().dump(test_outcome_integration_1)
    assert str(entities.TEST_OUTCOME_INTEGRATION_1_ID) == data["id"]
    assert test_outcome_integration_1.table == data["table"]
    assert sorted(test_outcome_integration_1.columns) == sorted(data["columns"])
    assert isinstance(data["columns"][0], str)
    assert isinstance(data["test_parameters"][0], dict)
    assert [{"name": "attr-1", "value": "1.0"}, {"name": "attr-2", "value": "v1"}] == data["test_parameters"]
    assert Integration.TESTGEN.name == data["integration_name"]


@pytest.mark.integration
def test_test_outcome_item_with_integration_dump(test_outcome, test_outcome_integration_1):
    data = TestOutcomeItemSchema().dump(test_outcome)
    assert "test-outcome-1" == data["name"]
    assert "test-outcome-key-1" == data["key"]

    integrations = data["integrations"]
    assert len(integrations) == 1

    integration_1 = integrations[0]
    assert str(entities.TEST_OUTCOME_INTEGRATION_1_ID) == integration_1["id"]
    assert [{"value": "1.0", "name": "attr-1"}, {"value": "v1", "name": "attr-2"}] == integration_1["test_parameters"]
    assert Integration.TESTGEN.name == integration_1["integration_name"]
