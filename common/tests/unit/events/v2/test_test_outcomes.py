from datetime import datetime, timezone, UTC
from decimal import Decimal

import pytest
from marshmallow.exceptions import ValidationError

from common.events.v2 import (
    TestGenBatchPipelineData,
    TestGenComponentData,
    TestOutcomeItem,
    TestOutcomesSchema,
    TestStatus,
)
from testlib.fixtures.v2_events import *


@pytest.fixture
def test_outcomes_testgen_data(test_outcomes_testgen_event_v2):
    return TestOutcomesSchema().dump(test_outcomes_testgen_event_v2.event_payload)


@pytest.fixture
def default_test_outcome_item_data():
    return {
        "name": "test name",
        "status": TestStatus.PASSED.name,
    }


@pytest.fixture
def test_outcome_items_dicts():
    return [
        {
            "name": f"test{i}",
            "metadata": {"vid": 1234},
            "status": TestStatus.PASSED.name,
            "description": f"Test{i} description",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "metric_value": 10.0 * i,
            "metric_name": "test metric name",
            "metric_description": "test metric desc",
            "metric_min_threshold": -100.0,
            "metric_max_threshold": 100.0,
            "integrations": None,
            "dimensions": ["a", "b"],
            "result": "test result",
            "type": "test type",
            "key": "test key",
        }
        for i in range(5)
    ]


@pytest.fixture
def test_outcome_items(test_outcome_items_dicts):
    return [TestOutcomeItem(**t) for t in test_outcome_items_dicts]


@pytest.fixture
def default_testgen_component_data(batch_pipeline_dict):
    return TestGenComponentData(
        batch_pipeline=TestGenBatchPipelineData(
            batch_key=batch_pipeline_dict["batch_key"],
            run_key=batch_pipeline_dict["run_key"],
            run_name=None,
            task_key=None,
            task_name=None,
            details=None,
            integrations=None,
        ),
        dataset=None,
        server=None,
        stream=None,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "outcome_item, match_value",
    (
        ([], "test_outcomes"),
        ([{"name": "a name"}], "status"),
        ([{"name": "a name", "status": "invalid status"}], "status"),
        ([{"status": TestStatus.WARNING.name}], "name"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "start_time": "invalid time"}], "start_time"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "end_time": "invalid time"}], "end_time"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "metric_value": "asdf"}], "metric_value"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "metric_name": ""}], "metric_name"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "metric_description": ""}], "metric_description"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "metric_min_threshold": "asdf"}], "metric_min_threshold"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "dimensions": []}], "dimensions"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "result": ""}], "result"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "type": ""}], "type"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "key": ""}], "key"),
        ([{"name": "a", "status": TestStatus.WARNING.name, "integrations": {"invalid": 1}}], "integrations"),
    ),
)
def test_test_outcomes_invalid(
    component_data_dict,
    outcome_item,
    match_value,
):
    with pytest.raises(ValidationError, match=match_value):
        TestOutcomesSchema().load({"test_outcomes": outcome_item, "component": component_data_dict})


@pytest.mark.unit
def test_default_test_outcomes(
    default_testgen_component_data,
    component_data_dict,
    default_test_outcome_item_data,
):
    res = TestOutcomesSchema().load(
        {"test_outcomes": [default_test_outcome_item_data], "component": component_data_dict}
    )
    assert res.component == default_testgen_component_data
    assert len(res.test_outcomes) == 1
    actual = res.test_outcomes[0]
    assert actual.name == default_test_outcome_item_data["name"]
    assert actual.status == TestStatus[default_test_outcome_item_data["status"]]
    assert actual.description == ""
    assert actual.start_time is None
    assert actual.end_time is None
    assert actual.metric_value is None
    assert actual.metric_name is None
    assert actual.metric_description is None
    assert actual.metric_min_threshold is None
    assert actual.metric_max_threshold is None
    assert actual.integrations is None
    assert actual.dimensions is None
    assert actual.result is None
    assert actual.type is None
    assert actual.key is None


@pytest.mark.unit
def test_testoutcomes_testgen_none_values(test_outcomes_testgen_data):
    test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]["tables"]["include_list"] = None
    test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]["tables"]["exclude_pattern"] = None
    test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]["table_group_configuration"][
        "uses_sampling"
    ] = None
    test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]["table_group_configuration"][
        "sample_percentage"
    ] = None
    test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]["table_group_configuration"][
        "sample_minimum_count"
    ] = None
    test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]["schema"] = None
    test_outcomes_testgen_data["test_outcomes"][0]["integrations"]["testgen"]["test_parameters"] = None
    TestOutcomesSchema().load(test_outcomes_testgen_data)
    test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]["table_group_configuration"] = None
    TestOutcomesSchema().load(test_outcomes_testgen_data)


@pytest.mark.unit
def test_test_outcomes(
    default_testgen_component_data,
    component_data_dict,
    test_outcome_items_dicts,
    test_outcome_items,
):
    res = TestOutcomesSchema().load(
        {
            "test_outcomes": test_outcome_items_dicts,
            "component": component_data_dict,
        }
    )
    assert res.component == default_testgen_component_data
    assert len(res.test_outcomes) == 5
    for actual, expected in zip(res.test_outcomes, test_outcome_items):
        assert actual.name == expected.name
        assert actual.description == expected.description
        assert actual.start_time == datetime.fromisoformat(expected.start_time).replace(tzinfo=UTC)
        assert actual.end_time == datetime.fromisoformat(expected.end_time).replace(tzinfo=UTC)
        assert actual.metric_value == expected.metric_value
        assert actual.metric_name == expected.metric_name
        assert actual.metric_description == expected.metric_description
        assert actual.metric_min_threshold == expected.metric_min_threshold
        assert actual.metric_max_threshold == expected.metric_max_threshold
        assert actual.dimensions == expected.dimensions
        assert actual.result == expected.result
        assert actual.type == expected.type
        assert actual.key == expected.key


@pytest.mark.unit
def test_testoutcomes_schema_with_testgen_integration(test_outcomes_testgen_data):
    event = TestOutcomesSchema().load(test_outcomes_testgen_data)
    integration_data = test_outcomes_testgen_data["component"]["dataset"]["integrations"]["testgen"]
    integration_event = event.component.dataset.integrations.testgen
    assert integration_event.version == integration_data["version"]
    assert integration_event.database_name == integration_data["database_name"]
    assert integration_event.connection_name == integration_data["connection_name"]
    assert integration_event.tables.include_list == integration_data["tables"]["include_list"]

    item_integration_data = test_outcomes_testgen_data["test_outcomes"][0]["integrations"]["testgen"]
    item_integration_event = event.test_outcomes[0].integrations.testgen
    assert item_integration_event.table == item_integration_data["table"]
    assert item_integration_event.test_suite == item_integration_data["test_suite"]
    assert item_integration_event.version == item_integration_data["version"]
    assert len(item_integration_event.test_parameters) == len(item_integration_data["test_parameters"])
    assert type(item_integration_event.test_parameters[0].value) == Decimal, (
        "expected dataclass's value to be Decimal type"
    )
    assert str(item_integration_event.test_parameters[0].value) == item_integration_data["test_parameters"][0]["value"]
    assert item_integration_event.test_parameters[0].name == item_integration_data["test_parameters"][0]["name"]
    assert item_integration_event.columns == item_integration_data["columns"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "required_field",
    (
        "component.dataset.integrations",
        "component.dataset.integrations.testgen",
        "component.dataset.integrations.testgen.version",
        "component.dataset.integrations.testgen.database_name",
        "component.dataset.integrations.testgen.connection_name",
        "component.dataset.integrations.testgen.tables",
        "component.dataset.integrations.testgen.table_group_configuration.group_id",
        "component.dataset.integrations.testgen.table_group_configuration.project_code",
        "test_outcomes.0.integrations.testgen",
        "test_outcomes.0.integrations.testgen.table",
        "test_outcomes.0.integrations.testgen.test_suite",
        "test_outcomes.0.integrations.testgen.version",
        "test_outcomes.0.integrations.testgen.test_parameters.0.name",
        "test_outcomes.0.integrations.testgen.test_parameters.0.value",
        # these two aren't required directly by schema, but fail due to validate_integration_present
        "component.dataset.integrations",
        "test_outcomes.0.integrations",
    ),
)
def test_testoutcomes_testgen_validate_required_fields(test_outcomes_testgen_data, required_field):
    keys = required_field.split(".")
    obj = test_outcomes_testgen_data
    for key in keys[:-1]:
        if isinstance(obj, dict):
            obj = obj[key]
        else:
            obj = obj[int(key)]
    key = keys[-1]
    if isinstance(obj, dict):
        obj = obj.pop(key)
    else:
        obj = obj.pop(int(key))
    with pytest.raises(ValidationError, match=key):
        TestOutcomesSchema().load(test_outcomes_testgen_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    "optional_field",
    (
        "component.dataset.integrations.testgen.schema",
        "component.dataset.integrations.testgen.table_group_configuration",
        "component.dataset.integrations.testgen.table_group_configuration.uses_sampling",
        "component.dataset.integrations.testgen.table_group_configuration.sample_percentage",
        "component.dataset.integrations.testgen.table_group_configuration.sample_minimum_count",
        "component.dataset.integrations.testgen.tables.exclude_pattern",
        "component.dataset.integrations.testgen.tables.include_pattern",
        "component.dataset.integrations.testgen.tables.include_list",
        "test_outcomes.0.integrations.testgen.columns",
    ),
)
def test_testoutcomes_testgen_validate_optional_fields(test_outcomes_testgen_data, optional_field):
    keys = optional_field.split(".")
    obj = test_outcomes_testgen_data
    for key in keys[:-1]:
        if isinstance(obj, dict):
            obj = obj[key]
        else:
            obj = obj[int(key)]
    key = keys[-1]
    if isinstance(obj, dict):
        obj = obj.pop(key)
    else:
        obj = obj.pop(int(key))
    evt_dataclass = TestOutcomesSchema().load(test_outcomes_testgen_data)
    TestOutcomesSchema().load(TestOutcomesSchema().dump(evt_dataclass))


@pytest.mark.unit
def test_testoutcomes_testgen_validate_table_include(test_outcomes_testgen_data):
    integrations = test_outcomes_testgen_data["component"]["dataset"]["integrations"]
    testgen = integrations["testgen"]
    tables = testgen["tables"]

    include_list = tables.pop("include_list")
    evt = TestOutcomesSchema().load(test_outcomes_testgen_data)
    assert evt.component.dataset.integrations.testgen.tables.include_list == []
    tables.pop("include_pattern")
    with pytest.raises(ValidationError, match=r"include_list.*include_pattern"):
        TestOutcomesSchema().load(test_outcomes_testgen_data)
    tables["include_list"] = []
    with pytest.raises(ValidationError, match=r"include_list.*include_pattern"):
        TestOutcomesSchema().load(test_outcomes_testgen_data)
    tables["include_list"] = include_list
    TestOutcomesSchema().load(test_outcomes_testgen_data)
