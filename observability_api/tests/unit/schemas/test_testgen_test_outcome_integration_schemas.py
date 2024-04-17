from decimal import Decimal

import pytest

from observability_api.schemas import TestgenItemTestParametersSchema


@pytest.mark.unit
def test_testgen_item_parameters_dump():
    data = TestgenItemTestParametersSchema().dump({"name": "my-attr", "value": Decimal("10.0")})
    expected = {"value": "10.0", "name": "my-attr"}
    assert expected == data
