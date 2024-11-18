__all__ = [
    "TestGenTestOutcomeIntegrations",
    "TestGenTestOutcomeIntegrationsSchema",
    "TestOutcomeItemIntegrations",
    "TestOutcomeItemIntegrationsSchema",
    "TestgenDataset",
    "TestgenIntegrationVersions",
    "TestgenItem",
    "TestgenItemTestParameters",
    "TestgenTable",
    "TestgenTableGroupV1",
]

from dataclasses import asdict, dataclass
from decimal import Decimal as std_Decimal
from enum import IntEnum
from typing import Any, Optional, Union
from uuid import UUID as std_UUID

from marshmallow import Schema, ValidationError, post_load, validates_schema
from marshmallow.fields import UUID, Bool, Decimal, Enum, Int, List, Nested, Str
from marshmallow_union import Union as UnionField

from common.schemas.validators import not_empty


class TestgenIntegrationVersions(IntEnum):
    V1 = 1


@dataclass
class TestgenItemTestParameters:
    name: str
    value: std_Decimal | str

    @property
    def json_dict(self) -> dict[str, Union[str, float, int]]:
        """Returns a dict that can be dumped as json."""
        data = asdict(self)
        updated = {}
        for k, v in data.items():
            if isinstance(v, std_Decimal):
                value: Union[str, float, int]
                as_tuple = v.as_tuple()
                if len(as_tuple.digits) == 1 and as_tuple.exponent == 0:
                    value = int(v)
                else:
                    value = float(v)
            elif isinstance(v, str | float | int):
                value = v
            else:
                raise TypeError(f"Got unexpected type {type(v)} for value {v}")
            updated[k] = value
        return updated


@dataclass
class TestgenItem:
    table: str
    test_suite: str
    version: TestgenIntegrationVersions
    test_parameters: list[TestgenItemTestParameters]
    columns: Optional[list[str]]


@dataclass
class TestOutcomeItemIntegrations:
    testgen: TestgenItem


@dataclass
class TestgenTable:
    include_list: list[str]
    include_pattern: Optional[str]
    exclude_pattern: Optional[str]


@dataclass
class TestgenTableGroupV1:
    group_id: std_UUID
    project_code: str
    uses_sampling: Optional[bool]
    sample_percentage: Optional[str]
    sample_minimum_count: Optional[int]


@dataclass
class TestgenDataset:
    version: TestgenIntegrationVersions
    database_name: str
    connection_name: str
    tables: TestgenTable
    schema: Optional[str]
    table_group_configuration: Optional[TestgenTableGroupV1]


@dataclass
class TestGenTestOutcomeIntegrations:
    testgen: TestgenDataset


class TestgenItemTestParametersSchema(Schema):
    name = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The name of the parameter"},
    )
    value = UnionField(
        fields=[Decimal(allow_nan=False, as_string=True), Str(validate=not_empty())],
        required=True,
        reverse_serialize_candidates=True,
        metadata={
            "description": "Required. The value of the parameter. Accepts a number or a string.",
        },
    )

    @post_load
    def to_testgen_item_test_parameters(self, data: dict, **_: Any) -> TestgenItemTestParameters:
        return TestgenItemTestParameters(**data)


class TestgenItemSchema(Schema):
    table = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. Name of the table the test was conducted on."},
    )
    columns = List(
        Str(allow_none=False, validate=not_empty()),
        required=False,
        allow_none=True,
        load_default=list,
        metadata={"description": "Optional. The name(s) of the table column(s) the test was conducted on."},
    )
    test_suite = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The name of the test suite the test is a member of."},
    )
    version = Enum(
        TestgenIntegrationVersions,
        by_value=True,
        required=True,
        metadata={"description": "Required. The integration schema version."},
    )
    test_parameters = Nested(
        TestgenItemTestParametersSchema,
        many=True,
        required=False,
        load_default=list,
        allow_none=True,
        metadata={
            "description": "Optional. An arbitrary list of test parameter descriptions. Defaults to an empty list."
        },
    )

    @post_load
    def to_testgen_item(self, data: dict, **_: Any) -> TestgenItem:
        return TestgenItem(**data)


class TestOutcomeItemIntegrationsSchema(Schema):
    testgen = Nested(
        TestgenItemSchema(),
        required=True,
        metadata={"description": "Required. Component data specific to DataKitchen Inc. Testgen integration."},
    )

    @post_load
    def to_testoutcome_item_integrations(self, data: dict, **_: Any) -> TestOutcomeItemIntegrations:
        return TestOutcomeItemIntegrations(**data)


class TestgenTableSchema(Schema):
    include_list = List(
        Str(allow_none=False, validate=not_empty()),
        required=False,
        load_default=list,
        allow_none=True,
        metadata={
            "description": (
                "Optional. The full names of tables explicitly included. Must specify at least one of "
                "`include_list` or `include_pattern`."
            )
        },
    )
    include_pattern = Str(
        required=False,
        load_default=None,
        validate=not_empty(),
        metadata={
            "description": (
                "Optional. The case insensitive pattern of included tables. Must specify at least one of "
                "`include_list` or `include_pattern`."
            )
        },
    )
    exclude_pattern = Str(
        required=False,
        load_default=None,
        validate=not_empty(),
        metadata={"description": ("Optional. The case insensitive pattern of excluded tables.")},
    )

    @validates_schema
    def validate_include(self, data: dict, **_: object) -> None:
        if not data.get("include_list") and not data.get("include_pattern"):
            raise ValidationError(
                {
                    "include_list": "Missing data for included tables. Must specify at least one of `include_list` or `include_pattern`.",
                    "include_pattern": "Missing data for included tables. Must specify at least one of `include_list` or `include_pattern`.",
                }
            )

    @post_load
    def to_testgen_table(self, data: dict, **_: Any) -> TestgenTable:
        return TestgenTable(**data)


class TestgenTableGroupV1Schema(Schema):
    group_id = UUID(
        required=True,
        metadata={"description": "Required. The ID of the table group."},
    )
    project_code = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The project code associated with the table group."},
    )
    uses_sampling = Bool(
        required=False,
        load_default=False,
        allow_none=True,
        metadata={
            "description": "Optional. Event comes from a Table Group that uses a sampling of data. Defaults to false."
        },
    )
    sample_percentage = Str(
        required=False,
        load_default=None,
        validate=not_empty(),
        metadata={"description": "Optional. Requires use_sampling. Percentage of sampling."},
    )
    sample_minimum_count = Int(
        required=False,
        load_default=None,
        metadata={"description": "Optional. Requires use_sampling. Minimum number of samples."},
    )

    @post_load
    def to_testgen_table_group(self, data: dict, **_: Any) -> TestgenTableGroupV1:
        return TestgenTableGroupV1(**data)


class TestgenDatasetSchema(Schema):
    version = Enum(
        TestgenIntegrationVersions,
        by_value=True,
        required=True,
        metadata={"description": "Required. Version of the integration."},
    )
    database_name = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The name of the database."},
    )
    connection_name = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The name of the connection according to Testgen."},
    )
    schema = Str(
        required=False,
        load_default=None,
        validate=not_empty(),
        metadata={"description": "Optional. The database schema."},
    )
    tables = Nested(
        TestgenTableSchema(),
        required=True,
        metadata={"description": "Required. The tables under test."},
    )
    table_group_configuration = Nested(
        TestgenTableGroupV1Schema(),
        required=False,
        load_default=None,
        metadata={"description": "Optional. Description of the table group."},
    )

    @post_load
    def to_testgen_dataset(self, data: dict, **_: Any) -> TestgenDataset:
        return TestgenDataset(**data)


class TestGenTestOutcomeIntegrationsSchema(Schema):
    testgen = Nested(
        TestgenDatasetSchema(),
        required=True,
        metadata={"description": ("Required. Component data specific to DataKitchen Inc. Testgen integration.")},
    )

    @post_load
    def to_test_outcome_integrations(self, data: dict, **_: Any) -> TestGenTestOutcomeIntegrations:
        return TestGenTestOutcomeIntegrations(**data)
