__all__ = [
    "TestgenIntegrationVersions",
    "TestOutcomeItem",
    "TestOutcomeItemIntegrations",
    "TestOutcomeItemSchema",
    "TestOutcomesSchema",
    "TestOutcomesApiSchema",
    "TestOutcomesEvent",
    "TestStatuses",
    "TestgenDataset",
    "TestGenTestOutcomeIntegrationComponent",
    "TestgenItemTestParametersSchema",
    "TestgenTable",
    "TestgenTableGroupV1",
    "TestgenItem",
    "TestgenItemTestParameters",
    "TestGenTestOutcomeIntegrations",
]

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal as std_decimal
from enum import Enum as std_Enum
from enum import IntEnum as std_IntEnum
from typing import Any, Optional, Union
from uuid import UUID as std_UUID

from marshmallow import Schema, ValidationError, post_load, validates_schema
from marshmallow.fields import UUID, AwareDateTime, Boolean, Decimal, Dict, Enum, Integer, List, Nested, Str
from marshmallow.validate import Length
from marshmallow_union import Union as UnionField

from common.constants import MAX_TEST_OUTCOME_ITEM_COUNT
from common.events.event_handler import EventHandlerBase
from common.events.v1.event import Event
from common.events.v1.event_schemas import EventApiSchema, EventSchema
from common.schemas.fields import EnumStr
from common.schemas.validators import not_empty


class TestStatuses(std_Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


class TestgenIntegrationVersions(std_IntEnum):
    V1 = 1


@dataclass
class TestgenItemTestParameters:
    name: str
    value: std_decimal | str

    @property
    def json_dict(self) -> dict[str, Union[str, float, int]]:
        """Returns a dict that can be dumped as json."""
        data = asdict(self)
        updated = {}
        for k, v in data.items():
            if isinstance(v, std_decimal):
                value: Union[str, float, int]
                as_tuple = v.as_tuple()
                if len(as_tuple.digits) == 1 and as_tuple.exponent == 0:
                    value = int(v)
                else:
                    value = float(v)
            elif isinstance(v, (str, float, int)):
                value = v
            else:
                raise TypeError(f"Got unexpected type {type(v)} for value {v}")
            updated[k] = value
        return updated


class TestgenItemTestParametersSchema(Schema):
    name = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The name of the parameter"},
    )
    value = UnionField(
        fields=[Decimal(allow_nan=False), Str(validate=not_empty())],
        required=True,
        reverse_serialize_candidates=True,
        metadata={
            "description": "Required. The value of the parameter. Accepts a number or a string.",
        },
    )

    @post_load
    def to_testgen_item_test_parameters(self, data: dict, **_: Any) -> TestgenItemTestParameters:
        return TestgenItemTestParameters(**data)


@dataclass
class TestgenItem:
    table: str
    test_suite: str
    version: int
    test_parameters: list[TestgenItemTestParameters]
    columns: Optional[list[str]] = None


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


@dataclass
class TestOutcomeItemIntegrations:
    testgen: TestgenItem


class TestOutcomeItemIntegrationsSchema(Schema):
    testgen = Nested(
        TestgenItemSchema(),
        required=True,
        metadata={"description": "Required. Component data specific to DataKitchen Inc. Testgen integration."},
    )

    @post_load
    def to_testoutcome_item_integrations(self, data: dict, **_: Any) -> TestOutcomeItemIntegrations:
        return TestOutcomeItemIntegrations(**data)


@dataclass
class TestgenTable:
    include_list: list[str]
    include_pattern: Optional[str] = None
    exclude_pattern: Optional[str] = None


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
        allow_none=True,
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
        allow_none=True,
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


@dataclass
class TestgenTableGroupV1:
    group_id: std_UUID
    project_code: str
    uses_sampling: Optional[bool] = None
    sample_percentage: Optional[str] = None
    sample_minimum_count: Optional[int] = None


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
    uses_sampling = Boolean(
        required=False,
        load_default=False,
        allow_none=True,
        metadata={
            "description": "Optional. Event comes from a Table Group that uses a sampling of data. Defaults to false."
        },
    )
    sample_percentage = Str(
        required=False,
        allow_none=True,
        validate=not_empty(),
        metadata={"description": "Optional. Requires use_sampling. Percentage of sampling."},
    )
    sample_minimum_count = Integer(
        required=False,
        allow_none=True,
        metadata={"description": "Optional. Requires use_sampling. Minimum number of samples."},
    )

    @post_load
    def to_testgen_table_group(self, data: dict, **_: Any) -> TestgenTableGroupV1:
        return TestgenTableGroupV1(**data)


@dataclass
class TestgenDataset:
    version: int
    database_name: str
    connection_name: str
    tables: TestgenTable
    schema: Optional[str] = None
    table_group_configuration: Optional[TestgenTableGroupV1] = None


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
        allow_none=True,
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
        allow_none=True,
        metadata={"description": "Optional. Description of the table group."},
    )

    @post_load
    def to_testgen_dataset(self, data: dict, **_: Any) -> TestgenDataset:
        return TestgenDataset(**data)


@dataclass
class TestGenTestOutcomeIntegrations:
    testgen: TestgenDataset


class TestGenTestOutcomeIntegrationsSchema(Schema):
    testgen = Nested(
        TestgenDatasetSchema(),
        required=True,
        metadata={"description": ("Required. Component data specific to DataKitchen Inc. Testgen integration.")},
    )

    @post_load
    def to_test_outcome_integrations(self, data: dict, **_: Any) -> TestGenTestOutcomeIntegrations:
        return TestGenTestOutcomeIntegrations(**data)


@dataclass
class TestGenTestOutcomeIntegrationComponent:
    integrations: TestGenTestOutcomeIntegrations


class TestGenTestOutcomeIntegrationComponentSchema(Schema):
    integrations = Nested(
        TestGenTestOutcomeIntegrationsSchema(),
        required=True,
        metadata={"description": ("Required. Component data specific to DataKitchen Inc. product Integrations.")},
    )

    @post_load
    def to_test_outcome_integration_component(self, data: dict, **_: Any) -> TestGenTestOutcomeIntegrationComponent:
        return TestGenTestOutcomeIntegrationComponent(**data)


@dataclass
class TestOutcomeItem:
    name: str
    status: str
    description: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None
    metric_value: Optional[Decimal] = None
    metric_name: Optional[str] = None
    metric_description: Optional[str] = None
    min_threshold: Optional[Decimal] = None
    max_threshold: Optional[Decimal] = None
    integrations: Optional[TestOutcomeItemIntegrations] = None
    dimensions: Optional[list[str]] = None
    result: Optional[str] = None
    type: Optional[str] = None
    key: Optional[str] = None


# region Schemas
class TestOutcomeItemSchema(Schema):
    name = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "The name of the test.", "example": "Health-check"},
    )
    status = EnumStr(
        required=True,
        enum=TestStatuses,
        metadata={
            "description": (
                "Required. The test status to be applied. Can set the status for both tests in runs and "
                "tests in tasks."
            )
        },
    )
    description = Str(
        allow_none=True,
        metadata={"description": "Optional. A description of the test outcomes.", "example": "System health check."},
    )
    start_time = AwareDateTime(
        format="iso",
        default_timezone=timezone.utc,
        allow_none=True,
        metadata={"description": "An ISO timestamp of when the test execution started."},
    )
    end_time = AwareDateTime(
        format="iso",
        default_timezone=timezone.utc,
        allow_none=True,
        metadata={"description": "An ISO timestamp of when the test execution ended."},
    )
    metric_value = Decimal(
        allow_none=True,
        allow_nan=False,
        # As string because Decimal is not serializable
        as_string=True,
        metadata={
            "description": ("Optional. A numerical test outcome."),
            "example": "20.4",
        },
    )
    metric_name = Str(
        validate=not_empty(),
        required=False,
        allow_none=True,
        metadata={"description": "Optional. The name of the metric, or its unit of measure."},
    )
    metric_description = Str(
        validate=not_empty(),
        required=False,
        allow_none=True,
        metadata={"description": "Optional. A description of the unit under measure."},
    )
    min_threshold = Decimal(
        allow_none=True,
        allow_nan=False,
        # As string because Decimal is not serializable
        as_string=True,
        metadata={
            "description": "Optional. The minimum acceptable value for the test metric_value",
            "example": "13.8",
        },
    )
    max_threshold = Decimal(
        allow_none=True,
        allow_nan=False,
        # As string because Decimal is not serializable
        as_string=True,
        metadata={
            "description": "Optional. The maximum acceptable value for the test metric_value.",
            "example": "27.8",
        },
    )
    metadata = Dict(
        load_default=dict,
        allow_none=True,
        metadata={
            "description": "Optional. Additional key-value information for the event. Provided by the user as needed.",
            "example": {"external_id": "2f107d18-1e2f-40f1-acf7-16d0bdd13a04"},
        },
    )
    integrations = Nested(
        TestOutcomeItemIntegrationsSchema(),
        required=False,
        allow_none=True,
        metadata={"description": "Optional. Test data specific to DataKitchen Inc. software integrations."},
    )
    dimensions = List(
        Str(
            allow_none=False,
            validate=not_empty(),
        ),
        required=False,
        allow_none=True,
        validate=not_empty(),
        metadata={"description": "Optional. Represents a list of data quality aspects the test is meant to address."},
    )
    result = Str(
        validate=not_empty(),
        required=False,
        allow_none=True,
        metadata={"description": "Optional. A string representing the tests' result."},
    )
    type = Str(
        validate=not_empty(),
        required=False,
        allow_none=True,
        metadata={"description": "Optional. Represents type or archetype of a test."},
    )
    key = Str(
        validate=not_empty(),
        required=False,
        allow_none=True,
        metadata={"description": "Optional. A correlation key. Tests with the same key are assumed to be related."},
    )

    @post_load
    def to_test_outcome_item(self, data: dict, **_: Any) -> TestOutcomeItem:
        return TestOutcomeItem(**data)


class TestOutcomesBaseSchema(Schema):
    test_outcomes = List(
        Nested(TestOutcomeItemSchema()),
        required=True,
        validate=Length(min=1, max=MAX_TEST_OUTCOME_ITEM_COUNT),
        metadata={"description": "Required. A list of objects, each representing the outcomes of a test."},
    )
    component_integrations = Nested(
        TestGenTestOutcomeIntegrationComponentSchema(),
        required=False,
        allow_none=True,
        metadata={"description": "Optional. Test Outcomes additional component data."},
    )

    @validates_schema
    def validate_integration_present(self, data: dict, **_: object) -> None:
        if data.get("component_integrations") and data["component_integrations"].integrations:
            if data["component_integrations"].integrations.testgen and not all(
                to.integrations and to.integrations.testgen for to in data["test_outcomes"]
            ):
                raise ValidationError(
                    {"test_outcomes[*].integrations.testgen": "Missing testgen integration for some items"}
                )
        else:
            if any(to.integrations and to.integrations.testgen for to in data["test_outcomes"]):
                raise ValidationError(
                    {
                        "component_integrations.integrations.testgen": "Missing testgen data from root payload when present for some items."
                    }
                )


class TestOutcomesSchema(TestOutcomesBaseSchema, EventSchema):
    pass


class TestOutcomesApiSchema(TestOutcomesBaseSchema, EventApiSchema):
    pass


# endregion
@dataclass
class TestOutcomesEvent(Event):
    """Represents the single result of a test."""

    test_outcomes: list[TestOutcomeItem]
    component_integrations: Optional[TestGenTestOutcomeIntegrationComponent] = None

    __schema__ = TestOutcomesSchema
    __api_schema__ = TestOutcomesApiSchema

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_test_outcomes(self)
