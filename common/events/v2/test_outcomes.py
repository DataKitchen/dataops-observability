__all__ = [
    "TestGenBatchPipelineData",
    "TestGenComponentData",
    "TestGenDatasetData",
    "TestGenServerData",
    "TestGenStreamData",
    "TestOutcomeItem",
    "TestOutcomes",
    "TestOutcomesSchema",
    "TestStatus",
    "TestOutcomesUserEvent",
]

from dataclasses import dataclass
from dataclasses import fields as dc_fields
from datetime import datetime, timezone
from decimal import Decimal as std_Decimal
from enum import Enum as std_Enum
from typing import Any, Optional

from marshmallow import Schema, ValidationError, post_load, validates_schema
from marshmallow.fields import AwareDateTime, Decimal, Dict, Enum, List, Nested, Str

from common.events.v2.testgen import (
    TestGenTestOutcomeIntegrations,
    TestGenTestOutcomeIntegrationsSchema,
    TestOutcomeItemIntegrations,
    TestOutcomeItemIntegrationsSchema,
)
from common.schemas.validators import not_empty

from ...entities.event import ApiEventType
from ..event_handler import EventHandlerBase
from .base import BasePayload, BasePayloadSchema, EventV2
from .component_data import (
    BatchPipelineData,
    BatchPipelineDataSchema,
    DatasetData,
    DatasetDataSchema,
    ServerData,
    ServerDataSchema,
    StreamData,
    StreamDataSchema,
)


class TestStatus(std_Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


@dataclass
class TestOutcomeItem:
    name: str
    status: TestStatus
    description: str
    metadata: dict[str, Any]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    metric_value: Optional[std_Decimal]
    metric_name: Optional[str]
    metric_description: Optional[str]
    metric_min_threshold: Optional[std_Decimal]
    metric_max_threshold: Optional[std_Decimal]
    integrations: Optional[TestOutcomeItemIntegrations]
    dimensions: Optional[list[str]]
    result: Optional[str]
    type: Optional[str]
    key: Optional[str]


@dataclass
class TestGenIntegrations:
    integrations: Optional[TestGenTestOutcomeIntegrations]


@dataclass
class TestGenBatchPipelineData(BatchPipelineData, TestGenIntegrations): ...


@dataclass
class TestGenDatasetData(DatasetData, TestGenIntegrations): ...


@dataclass
class TestGenServerData(ServerData, TestGenIntegrations): ...


@dataclass
class TestGenStreamData(StreamData, TestGenIntegrations): ...


@dataclass
class TestGenComponentData:
    batch_pipeline: Optional[TestGenBatchPipelineData]
    stream: Optional[TestGenStreamData]
    dataset: Optional[TestGenDatasetData]
    server: Optional[TestGenServerData]


@dataclass
class TestOutcomes(BasePayload):
    component: TestGenComponentData
    test_outcomes: list[TestOutcomeItem]


class TestGenIntegrationsSchema(Schema):
    integrations = Nested(
        TestGenTestOutcomeIntegrationsSchema(),
        load_default=None,
        required=False,
        metadata={"description": ("Required. Component data specific to DataKitchen Inc. product Integrations.")},
    )


class TestOutcomeItemSchema(Schema):
    name = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "The name of the test.", "example": "Health-check"},
    )
    status = Enum(
        required=True,
        enum=TestStatus,
        metadata={
            "description": (
                "Required. The test status to be applied. Can set the status for both tests in runs and "
                "tests in tasks."
            )
        },
    )
    description = Str(
        load_default="",
        metadata={"description": "Optional. A description of the test outcomes.", "example": "System health check."},
    )
    metadata = Dict(
        load_default=dict,
        allow_none=True,
        metadata={
            "description": "Optional. Additional key-value information for the test outcome item. Provided by the user as needed.",
            "example": {"external_id": "2f107d18-1e2f-40f1-acf7-16d0bdd13a04"},
        },
    )
    start_time = AwareDateTime(
        format="iso",
        default_timezone=timezone.utc,
        load_default=None,
        metadata={"description": "An ISO timestamp of when the test execution started."},
    )
    end_time = AwareDateTime(
        format="iso",
        default_timezone=timezone.utc,
        load_default=None,
        metadata={"description": "An ISO timestamp of when the test execution ended."},
    )
    metric_value = Decimal(
        load_default=None,
        allow_nan=False,
        as_string=True,
        metadata={
            "description": ("Optional. A numerical test outcome."),
            "example": "20.4",
        },
    )
    metric_name = Str(
        load_default=None,
        validate=not_empty(),
        required=False,
        metadata={"description": "Optional. The name of the metric, or its unit of measure."},
    )
    metric_description = Str(
        load_default=None,
        validate=not_empty(),
        required=False,
        metadata={"description": "Optional. A description of the unit under measure."},
    )
    metric_min_threshold = Decimal(
        load_default=None,
        allow_nan=False,
        as_string=True,
        metadata={
            "description": ("Optional. The minimum acceptable value for the test metric_value"),
            "example": "13.8",
        },
    )
    metric_max_threshold = Decimal(
        load_default=None,
        allow_nan=False,
        as_string=True,
        metadata={
            "description": ("Optional. The maximum acceptable value for the test metric_value."),
            "example": "27.8",
        },
    )
    integrations = Nested(
        TestOutcomeItemIntegrationsSchema(),
        required=False,
        load_default=None,
        metadata={"description": "Optional. Test data specific to DataKitchen Inc. software integrations."},
    )
    dimensions = List(
        Str(
            allow_none=False,
            validate=not_empty(),
        ),
        load_default=None,
        required=False,
        validate=not_empty(),
        metadata={"description": "Optional. Represents a list of data quality aspects the test is meant to address."},
    )
    result = Str(
        load_default=None,
        validate=not_empty(),
        required=False,
        metadata={"description": "Optional. A string representing the tests' result."},
    )
    type = Str(
        load_default=None,
        validate=not_empty(),
        required=False,
        metadata={"description": "Optional. Represents type or archetype of a test."},
    )
    key = Str(
        load_default=None,
        validate=not_empty(),
        required=False,
        metadata={"description": "Optional. A correlation key. Tests with the same key are assumed to be related."},
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> TestOutcomeItem:
        return TestOutcomeItem(**data)


class TestGenBatchPipelineDataSchema(BatchPipelineDataSchema, TestGenIntegrationsSchema):
    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> TestGenBatchPipelineData:
        return TestGenBatchPipelineData(**data)


class TestGenDatasetDataSchema(DatasetDataSchema, TestGenIntegrationsSchema):
    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> TestGenDatasetData:
        return TestGenDatasetData(**data)


class TestGenServerDataSchema(ServerDataSchema, TestGenIntegrationsSchema):
    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> TestGenServerData:
        return TestGenServerData(**data)


class TestGenStreamDataSchema(StreamDataSchema, TestGenIntegrationsSchema):
    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> TestGenStreamData:
        return TestGenStreamData(**data)


class TestGenComponentDataSchema(Schema):
    batch_pipeline = Nested(
        TestGenBatchPipelineDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. The target batch pipeline for the event action.",
        },
    )
    stream = Nested(
        TestGenStreamDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. The target stream for the event action.",
        },
    )
    dataset = Nested(
        TestGenDatasetDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. The target dataset for the event action.",
        },
    )
    server = Nested(
        TestGenServerDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. The target server for the event action.",
        },
    )

    @validates_schema
    def validate_keys(self, data: dict, **_: object) -> None:
        if sum(1 for v in data.values() if v is not None) != 1:
            raise ValidationError("Exactly one component must be given")

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> TestGenComponentData:
        return TestGenComponentData(**data)


class TestOutcomesSchema(BasePayloadSchema):
    component = Nested(
        TestGenComponentDataSchema,
        required=True,
        metadata={"description": "Required. The component associated to the test outcomes."},
    )
    test_outcomes = Nested(
        TestOutcomeItemSchema,
        required=True,
        validate=not_empty(),
        many=True,
        metadata={
            "description": "Required. A list of objects, where each key-value describes a part of the test outcomes."
        },
    )

    @validates_schema
    def validate_integration_present(self, data: dict, **_: object) -> None:
        components = data["component"]
        if integrations := next(
            c for f in dc_fields(components) if (c := getattr(components, f.name, None))
        ).integrations:
            if integrations.testgen and not all(
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

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> TestOutcomes:
        return TestOutcomes(**data)


@dataclass(kw_only=True)
class TestOutcomesUserEvent(EventV2):
    event_payload: TestOutcomes
    event_type: ApiEventType = ApiEventType.TEST_OUTCOMES

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_test_outcomes_v2(self)
