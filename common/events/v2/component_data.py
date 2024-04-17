__all__ = [
    "BatchPipelineData",
    "BatchPipelineDataSchema",
    "ComponentData",
    "ComponentDataSchema",
    "DatasetData",
    "DatasetDataSchema",
    "DatasetDataSchema",
    "NewComponentData",
    "NewComponentDataSchema",
    "ServerData",
    "ServerDataSchema",
    "StreamData",
    "StreamDataSchema",
]

from dataclasses import dataclass
from typing import Any, Optional

from marshmallow import Schema, ValidationError, post_load, validates_schema
from marshmallow.fields import Nested, Str
from marshmallow.validate import Regexp

from common.constants import EXTENDED_ALPHANUMERIC_REGEX, INVALID_TOOL_VALUE, MAX_COMPONENT_TOOL_LENGTH
from common.schemas.fields import NormalizedStr, strip_upper_underscore
from common.schemas.validators import not_empty


@dataclass
class NewComponentData:
    name: Optional[str]
    tool: Optional[str]


@dataclass
class BatchPipelineData:
    batch_key: str
    run_key: str
    run_name: Optional[str]
    task_key: Optional[str]
    task_name: Optional[str]
    details: Optional[NewComponentData]


@dataclass
class DatasetData:
    dataset_key: str
    details: Optional[NewComponentData]


@dataclass
class ServerData:
    server_key: str
    details: Optional[NewComponentData]


@dataclass
class StreamData:
    stream_key: str
    details: Optional[NewComponentData]


@dataclass
class ComponentData:
    batch_pipeline: Optional[BatchPipelineData]
    stream: Optional[StreamData]
    dataset: Optional[DatasetData]
    server: Optional[ServerData]


class NewComponentDataSchema(Schema):
    name = Str(
        load_default=None,
        metadata={
            "description": "Optional. Human readable display name for the pipeline.",
            "example": "UI Test Batch Pipeline",
        },
    )
    tool = NormalizedStr(
        required=False,
        load_default=None,
        normalizer=strip_upper_underscore,
        validate=[
            Regexp(EXTENDED_ALPHANUMERIC_REGEX, error=INVALID_TOOL_VALUE),
            not_empty(max=MAX_COMPONENT_TOOL_LENGTH),
        ],
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> NewComponentData:
        return NewComponentData(**data)


class BatchPipelineDataSchema(Schema):
    batch_key = Str(
        required=True,
        metadata={
            "description": "Required. The identifier of the target batch pipeline.",
            "example": "897279df-9d37-4e82-8b14-2be4a6a2d9ab",
        },
    )
    run_key = Str(
        required=True,
        metadata={
            "description": ("Required. The identifier of the target run."),
            "example": "901b94a3-0c22-4089-b483-81981c893387",
        },
    )
    run_name = Str(
        load_default=None,
        metadata={
            "description": "Optional. Human readable display name for the run.",
            "example": "run 2023-02-15",
        },
    )
    task_key = Str(
        load_default=None,
        metadata={
            "description": (
                "Optional. The identifier for a run task. When no task_key is included, "
                "the event applies to the run specified by the run_key."
            ),
            "example": "7a6363c2-53d6-4759-b4e5-42e41b24791f",
        },
    )
    task_name = Str(
        load_default=None,
        metadata={
            "description": "Optional. A human-readable display name for the task.",
            "example": "Build Task",
        },
    )
    details = Nested(
        NewComponentDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. Additional batch pipeline details.",
        },
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> BatchPipelineData:
        return BatchPipelineData(**data)


class DatasetDataSchema(Schema):
    dataset_key = Str(
        required=True,
        metadata={
            "description": "Required. The identifier of the target dataset.",
            "example": "f0d6511e-4cdc-4d80-b8b8-0c991e2419c7",
        },
    )
    details = Nested(
        NewComponentDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. Additional dataset details.",
        },
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> DatasetData:
        return DatasetData(**data)


class ServerDataSchema(Schema):
    server_key = Str(
        required=True,
        metadata={
            "description": "Required. The identifier of the target server.",
            "example": "42c198a5-a066-4757-aca6-7296ab87cc86",
        },
    )
    details = Nested(
        NewComponentDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. Additional server details.",
        },
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> ServerData:
        return ServerData(**data)


class StreamDataSchema(Schema):
    stream_key = Str(
        required=True,
        metadata={
            "description": "Required. The identifier of the target stream.",
            "example": "e04e7fb3-046a-4d64-8a1d-70898b959f20",
        },
    )
    details = Nested(
        NewComponentDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. Additional stream details.",
        },
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> StreamData:
        return StreamData(**data)


class ComponentDataSchema(Schema):
    batch_pipeline = Nested(
        BatchPipelineDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. The target batch pipeline for the event action.",
        },
    )
    stream = Nested(
        StreamDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. The target stream for the event action.",
        },
    )
    dataset = Nested(
        DatasetDataSchema,
        load_default=None,
        metadata={
            "description": "Optional. The target dataset for the event action.",
        },
    )
    server = Nested(
        ServerDataSchema,
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
    def to_dataclass(self, data: dict, **_: Any) -> ComponentData:
        return ComponentData(**data)
