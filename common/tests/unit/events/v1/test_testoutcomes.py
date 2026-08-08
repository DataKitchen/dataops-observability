from decimal import Decimal

import pytest
from marshmallow import ValidationError

from common.events.v1.test_outcomes_event import TestOutcomesEvent, TestStatuses


@pytest.mark.unit
def test_testoutcomes_schema(test_outcomes_event_data):
    event = TestOutcomesEvent.from_dict(test_outcomes_event_data)
    item_data = test_outcomes_event_data["test_outcomes"][0]
    assert "test_outcomes" in test_outcomes_event_data
    assert len(event.test_outcomes) == 1
    assert event.test_outcomes[0].name == item_data["name"]
    assert event.test_outcomes[0].status == TestStatuses.PASSED.name
    assert event.test_outcomes[0].start_time.isoformat() == item_data["start_time"]
    assert event.test_outcomes[0].end_time.isoformat() == item_data["end_time"]
    assert event.test_outcomes[0].metadata == item_data["metadata"]
    assert event.test_outcomes[0].metric_value == Decimal(item_data["metric_value"])
    assert event.test_outcomes[0].min_threshold == Decimal(item_data["min_threshold"])
    assert event.test_outcomes[0].max_threshold == Decimal(item_data["max_threshold"])


@pytest.mark.unit
def test_testoutcomes_schema_with_testgen_integration(test_outcomes_testgen_event_data):
    event = TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)
    integration_data = test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"]
    integration_event = event.component_integrations.integrations.testgen
    assert integration_event.version == integration_data["version"]
    assert integration_event.database_name == integration_data["database_name"]
    assert integration_event.connection_name == integration_data["connection_name"]
    assert integration_event.tables.include_list == integration_data["tables"]["include_list"]

    item_integration_data = test_outcomes_testgen_event_data["test_outcomes"][0]["integrations"]["testgen"]
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
def test_testoutcomes_as_dict(test_outcomes_event_data):
    event = TestOutcomesEvent.from_dict(test_outcomes_event_data)
    event_data = event.as_dict()
    assert "test_outcomes" in event_data

    base_data = test_outcomes_event_data["test_outcomes"][0]
    serialized = event_data["test_outcomes"][0]

    assert serialized["min_threshold"] == str(base_data["min_threshold"])
    assert serialized["max_threshold"] == str(base_data["max_threshold"])
    assert serialized["metric_value"] == str(base_data["metric_value"])
    assert serialized["start_time"] == base_data["start_time"]
    assert event_data["task_key"] == test_outcomes_event_data["task_key"]


@pytest.mark.unit
def test_testoutcomes_validate_default_values(test_outcomes_event_data):
    test_outcomes_event_data.pop("task_key")
    event = TestOutcomesEvent.from_dict(test_outcomes_event_data)
    assert event.task_key is None


@pytest.mark.unit
def test_testoutcomes_testgen_none_values(test_outcomes_testgen_event_data):
    test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"]["tables"]["include_list"] = (
        None
    )
    test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"]["tables"][
        "exclude_pattern"
    ] = None
    test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"]["table_group_configuration"][
        "uses_sampling"
    ] = None
    test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"]["table_group_configuration"][
        "sample_percentage"
    ] = None
    test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"]["table_group_configuration"][
        "sample_minimum_count"
    ] = None
    test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"]["schema"] = None
    test_outcomes_testgen_event_data["test_outcomes"][0]["integrations"]["testgen"]["test_parameters"] = None
    TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)
    test_outcomes_testgen_event_data["component_integrations"]["integrations"]["testgen"][
        "table_group_configuration"
    ] = None
    TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)


@pytest.mark.unit
@pytest.mark.parametrize("required_field", ("test_outcomes",))
def test_testoutcomes_validate_required_fields(test_outcomes_event_data, required_field):
    test_outcomes_event_data.pop(required_field)
    with pytest.raises(ValidationError):
        TestOutcomesEvent.from_dict(test_outcomes_event_data)


@pytest.mark.unit
@pytest.mark.parametrize("amount, raises", ((500, False), (501, True)))
def test_testoutcomes_validate_item_count_limit(amount, raises, test_outcomes_event_data, test_outcome_item_data):
    event_data = test_outcomes_event_data.copy()
    event_data["test_outcomes"] = [test_outcome_item_data for _ in range(amount)]
    if raises:
        with pytest.raises(ValidationError):
            TestOutcomesEvent.from_dict(event_data)
    else:
        TestOutcomesEvent.from_dict(event_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    "required_field",
    (
        "component_integrations.integrations",
        "component_integrations.integrations.testgen",
        "component_integrations.integrations.testgen.version",
        "component_integrations.integrations.testgen.database_name",
        "component_integrations.integrations.testgen.connection_name",
        "component_integrations.integrations.testgen.tables",
        "component_integrations.integrations.testgen.table_group_configuration.group_id",
        "component_integrations.integrations.testgen.table_group_configuration.project_code",
        "test_outcomes.0.integrations.testgen",
        "test_outcomes.0.integrations.testgen.table",
        "test_outcomes.0.integrations.testgen.test_suite",
        "test_outcomes.0.integrations.testgen.version",
        "test_outcomes.0.integrations.testgen.test_parameters.0.name",
        "test_outcomes.0.integrations.testgen.test_parameters.0.value",
        # these two aren't required directly by schema, but fail due to validate_integration_present
        "component_integrations",
        "test_outcomes.0.integrations",
    ),
)
def test_testoutcomes_testgen_validate_required_fields(test_outcomes_testgen_event_data, required_field):
    keys = required_field.split(".")
    obj = test_outcomes_testgen_event_data
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
        TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    "optional_field",
    (
        "component_integrations.integrations.testgen.schema",
        "component_integrations.integrations.testgen.table_group_configuration",
        "component_integrations.integrations.testgen.table_group_configuration.uses_sampling",
        "component_integrations.integrations.testgen.table_group_configuration.sample_percentage",
        "component_integrations.integrations.testgen.table_group_configuration.sample_minimum_count",
        "component_integrations.integrations.testgen.tables.exclude_pattern",
        "component_integrations.integrations.testgen.tables.include_pattern",
        "component_integrations.integrations.testgen.tables.include_list",
        "test_outcomes.0.integrations.testgen.columns",
    ),
)
def test_testoutcomes_testgen_validate_optional_fields(test_outcomes_testgen_event_data, optional_field):
    keys = optional_field.split(".")
    obj = test_outcomes_testgen_event_data
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
    evt_dataclass = TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)
    TestOutcomesEvent.__schema__().load(evt_dataclass.as_dict())


@pytest.mark.unit
def test_testoutcomes_testgen_validate_table_include(test_outcomes_testgen_event_data):
    component_integrations = test_outcomes_testgen_event_data["component_integrations"]
    integrations = component_integrations["integrations"]
    testgen = integrations["testgen"]
    tables = testgen["tables"]

    include_list = tables.pop("include_list")
    evt = TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)
    assert evt.component_integrations.integrations.testgen.tables.include_list == []
    tables.pop("include_pattern")
    with pytest.raises(ValidationError, match=r"include_list.*include_pattern"):
        TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)
    tables["include_list"] = []
    with pytest.raises(ValidationError, match=r"include_list.*include_pattern"):
        TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)
    tables["include_list"] = include_list
    TestOutcomesEvent.from_dict(test_outcomes_testgen_event_data)
