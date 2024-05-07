from decimal import Decimal

import pytest

from common.events.v2.testgen import TestgenItemTestParameters


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
