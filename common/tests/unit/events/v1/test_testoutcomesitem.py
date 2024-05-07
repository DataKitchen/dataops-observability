import math
from decimal import Decimal

import pytest
from marshmallow import ValidationError

from common.events.v1 import TestOutcomeItemSchema, TestStatuses
from common.events.v1.test_outcomes_event import TestgenItemTestParameters


@pytest.mark.unit
@pytest.mark.parametrize("valid_status", [e.value for e in TestStatuses])
def test_load_outcomeitem(test_outcome_item_data, valid_status):
    test_outcome_item_data["status"] = valid_status
    result = TestOutcomeItemSchema().load(test_outcome_item_data)

    assert result.status == test_outcome_item_data["status"]
    assert result.name == test_outcome_item_data["name"]
    assert result.description == test_outcome_item_data["description"]
    assert result.start_time.isoformat() == test_outcome_item_data["start_time"]
    assert result.end_time.isoformat() == test_outcome_item_data["end_time"]
    assert result.metadata == test_outcome_item_data["metadata"]
    assert result.metric_value == test_outcome_item_data["metric_value"]
    assert result.min_threshold == test_outcome_item_data["min_threshold"]
    assert result.max_threshold == test_outcome_item_data["max_threshold"]


@pytest.mark.unit
def test_load_outcomeitem_status_insensitive(test_outcome_item_data):
    test_outcome_item_data["status"] = TestStatuses.FAILED.name.lower()
    result = TestOutcomeItemSchema().load(test_outcome_item_data)
    assert result.status == TestStatuses.FAILED.name


@pytest.mark.unit
@pytest.mark.parametrize("required_field", ("status", "name"))
def test_load_outcomeitem_required_fields_missing(test_outcome_item_data, required_field):
    test_outcome_item_data.pop(required_field)
    with pytest.raises(ValidationError):
        TestOutcomeItemSchema().load(test_outcome_item_data)


@pytest.mark.unit
def test_load_outcomeitem_default_values(test_outcome_item_data):
    defaults = {
        "description": "",
        "start_time": None,
        "end_time": None,
        "metric_value": None,
        "min_threshold": None,
        "max_threshold": None,
        "metadata": {},
    }
    event_data = {k: v for k, v in test_outcome_item_data.items() if k not in defaults}

    event_object = TestOutcomeItemSchema().load(event_data)

    for attr, value in defaults.items():
        assert getattr(event_object, attr) == value, f"TestOutcomeItem didn't have the proper default for '{attr}'"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("name", ""),
        ("max_threshold", math.inf),
        ("min_threshold", math.nan),
        ("metric_value", math.inf),
    ),
)
def test_load_outcomeitem_invalid_data(test_outcome_item_data, field, value):
    test_outcome_item_data[field] = value
    with pytest.raises(ValidationError):
        TestOutcomeItemSchema().load(test_outcome_item_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("instance", "expected"),
    (
        (TestgenItemTestParameters(name="foo", value=Decimal("1")), {"name": "foo", "value": 1}),
        (TestgenItemTestParameters(name="foo", value=1), {"name": "foo", "value": 1}),
        (TestgenItemTestParameters(name="foo", value=Decimal("1.1")), {"name": "foo", "value": 1.1}),
        (TestgenItemTestParameters(name="foo", value=1.1), {"name": "foo", "value": 1.1}),
        (TestgenItemTestParameters(name="foo", value=0), {"name": "foo", "value": 0}),
        (TestgenItemTestParameters(name="foo", value=Decimal("1.0")), {"name": "foo", "value": 1.0}),
    ),
)
def test_testgen_item_test_parameters_json_dict(instance, expected):
    actual = instance.json_dict
    assert expected == actual
    assert type(expected["value"]) is type(actual["value"])  # noqa: E721


@pytest.mark.unit
def test_testgen_item_test_parameters_json_dict_invalid():
    instance = TestgenItemTestParameters(name="foo", value=object())
    with pytest.raises(TypeError):
        instance.json_dict
