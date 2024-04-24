__all__ = [
    "TestOutcomeItemSchema",
    "TestGenTestOutcomeIntegrationSchema",
    "TestgenItemTestParametersSchema",
    "Integration",
]

from enum import Enum

from marshmallow import Schema
from marshmallow.fields import DateTime, Decimal, List, Nested, Str
from marshmallow_union import Union as UnionField

from common.entities import TestGenTestOutcomeIntegration, TestOutcome
from common.schemas.validators import not_empty
from observability_api.schemas.base_schemas import BaseEntitySchema
from observability_api.schemas.component_schemas import ComponentSchema


class TestgenItemTestParametersSchema(Schema):
    name = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": ("Required. The name of the parameter")},
    )
    value = UnionField(
        fields=[Decimal(allow_nan=False), Str(validate=not_empty())],
        required=True,
        reverse_serialize_candidates=True,
        metadata={
            "description": ("Required. The value of the parameter. Accepts a number or a string."),
        },
    )


class Integration(Enum):
    TESTGEN = "TESTGEN"


class TestGenTestOutcomeIntegrationSchema(BaseEntitySchema):
    columns = List(Str())
    test_parameters = List(Nested(TestgenItemTestParametersSchema()))
    integration_name = Str(dump_only=True, dump_default=Integration.TESTGEN.name)

    class Meta:
        model = TestGenTestOutcomeIntegration


class TestOutcomeItemSchema(BaseEntitySchema):
    start_time = DateTime(dump_only=True)
    end_time = DateTime(dump_only=True)
    component = Nested(ComponentSchema(only=("id", "type", "display_name", "tool")))
    dimensions = List(Str())
    metric_value = Decimal(
        required=False,
        allow_nan=False,
        as_string=True,  # As string because Decimal is not serializable
        metadata={
            "description": "Optional. The data value to be logged. Decimal numerals only; NaN/INF values not supported.",
            "example": 10.22,
        },
    )
    min_threshold = Decimal(
        required=False,
        allow_nan=False,
        as_string=True,
        metadata={
            "description": "Optional. The minimum threshold value for the test outcome. Decimal numerals only; NaN/INF values not supported.",
            "example": 3.14,
        },
    )
    max_threshold = Decimal(
        required=False,
        allow_nan=False,
        as_string=True,
        metadata={
            "description": "Optional. The maximum threshold value for the test outcome. Decimal numerals only; NaN/INF values not supported.",
            "example": 6.28,
        },
    )
    testgen_test_outcome_integrations = List(Nested(TestGenTestOutcomeIntegrationSchema()), data_key="integrations")

    class Meta:
        model = TestOutcome
