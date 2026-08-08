__all__ = ["EventSchemaInterface", "EventApiSchema", "EventSchema"]

import json
from datetime import UTC
from typing import Any, Union

from marshmallow import Schema, ValidationError, post_dump, post_load, pre_load, validates_schema
from marshmallow.fields import UUID, AwareDateTime, Dict, Enum, List, Nested, Str, Url
from marshmallow.validate import Regexp

from common.constants import (
    EXTENDED_ALPHANUMERIC_REGEX,
    INVALID_TOOL_VALUE,
    MAX_COMPONENT_NAME_LENGTH,
    MAX_COMPONENT_TOOL_LENGTH,
    MAX_PAYLOAD_KEY_LENGTH,
    MAX_PIPELINE_KEY_LENGTH,
    MAX_RUN_KEY_LENGTH,
    MAX_RUN_NAME_LENGTH,
    MAX_SUBCOMPONENT_KEY_LENGTH,
    MAX_TASK_KEY_LENGTH,
    MAX_TASK_NAME_LENGTH,
)
from common.constants.validation_messages import MISSING_COMPONENT_KEY, PIPELINE_EVENT_MISSING_REQUIRED_KEY
from common.entities.event import EventVersion
from common.schemas.fields import EnumStr, NormalizedStr, strip_upper_underscore
from common.schemas.validators import not_empty

from ..base import InstanceRef
from ..enums import EventSources


class EventSchemaInterface(Schema):
    @pre_load
    def decode_bytes(self, data: Union[dict, bytes], **_: Any) -> Union[dict, bytes]:
        if isinstance(data, bytes):
            data = json.loads(data.decode("utf-8"))
        return data

    @post_dump
    def remove_none_values(self, data: dict[str, Any], **kwargs: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in data.items() if value is not None}


class EventApiSchema(EventSchemaInterface):
    server_key = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_SUBCOMPONENT_KEY_LENGTH),
        metadata={
            "description": "The key identifier of the target server component for the event action. Only one component "
            "key can be provided at a time.",
            "example": "897279df-9d37-4e82-8b14-2be4a6a2d9ab",
        },
    )
    server_name = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_COMPONENT_NAME_LENGTH),
        metadata={
            "description": "Optional. Human readable display name for the server.",
            "example": "Azure server",
        },
    )
    stream_key = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_SUBCOMPONENT_KEY_LENGTH),
        metadata={
            "description": "The key identifier of the target streaming-pipeline for the event action. Only one "
            "component key can be provided at a time.",
            "example": "897279df-9d37-4e82-8b14-2be4a6a2d9ab",
        },
    )
    stream_name = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_COMPONENT_NAME_LENGTH),
        metadata={
            "description": "Optional. Human readable display name for the streaming-pipeline.",
            "example": "UI Test Streaming Pipeline",
        },
    )
    dataset_key = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_SUBCOMPONENT_KEY_LENGTH),
        metadata={
            "description": "The key identifier of the target dataset component for the event action. Only one component "
            "key can be provided at a time.",
            "example": "897279df-9d37-4e82-8b14-2be4a6a2d9ab",
        },
    )
    dataset_name = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_COMPONENT_NAME_LENGTH),
        metadata={
            "description": "Optional. Human readable display name for the dataset component.",
            "example": "Weather data",
        },
    )
    pipeline_key = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_PIPELINE_KEY_LENGTH),
        metadata={
            "description": "The key identifier of the target batch-pipeline component for the event action. Only one "
            "component key can be provided at a time.",
            "example": "897279df-9d37-4e82-8b14-2be4a6a2d9ab",
        },
    )
    pipeline_name = Str(
        load_default=None,
        required=False,
        validate=not_empty(max=MAX_COMPONENT_NAME_LENGTH),
        metadata={
            "description": "Optional. Human readable display name for the batch-pipeline component.",
            "example": "UI Test Pipeline",
        },
    )
    component_tool = NormalizedStr(
        required=False,
        load_default=None,
        normalizer=strip_upper_underscore,
        validate=[
            Regexp(EXTENDED_ALPHANUMERIC_REGEX, error=INVALID_TOOL_VALUE),
            not_empty(max=MAX_COMPONENT_TOOL_LENGTH),
        ],
    )
    external_url = Url(
        load_default=None,
        metadata={"description": "A link to source information.", "example": "https://example.com"},
    )
    run_key = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_RUN_KEY_LENGTH),
        metadata={
            "description": (
                "The identifier of the target run for the event action. This key is created and managed by the user. "
                "Required if the target component is a batch-pipeline. "
            ),
            "example": "Important",
        },
    )
    run_name = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_RUN_NAME_LENGTH),
        metadata={
            "description": "Optional. Human readable display name for the run.",
            "example": "run 2023-02-15",
        },
    )
    task_key = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_TASK_KEY_LENGTH),
        metadata={
            "description": (
                "Optional. The identifier for a run task. When no task_key is included, "
                "the event applies to the run specified by the run_key."
            ),
            "example": "18c469e7-db4c-45d4-9414-7c58f196e199",
        },
    )
    task_name = Str(
        required=False,
        load_default=None,
        validate=not_empty(max=MAX_TASK_NAME_LENGTH),
        metadata={
            "description": "Optional. A human-readable display name for the task.",
            "example": "Descriptive Name",
        },
    )
    event_timestamp = AwareDateTime(
        format="iso",
        default_timezone=UTC,
        metadata={
            "description": (
                "Optional. An ISO8601 timestamp that describes when the event occurred. If no timezone "
                "is specified, UTC is assumed. If unset, the Event Ingestion API applies its current time "
                "as the value."
            )
        },
    )
    metadata = Dict(
        load_default={},
        metadata={
            "description": "Optional. Additional key-value information for the event. Provided by the user as needed.",
            "example": {"external_id": "2f107d18-1e2f-40f1-acf7-16d0bdd13a04"},
        },
    )
    payload_keys = List(
        Str(validate=not_empty(max=MAX_PAYLOAD_KEY_LENGTH)),
        load_default=list,
        metadata={
            "description": "The key identifiers of the datums of interest.",
            "example": "[dataset-11, dataset-59]",
        },
    )

    @staticmethod
    def _get_component_keys(data: dict[str, Any]) -> list[str]:
        valid_component_keys = ["pipeline_key", "dataset_key", "server_key", "stream_key"]
        return [key for key in valid_component_keys if data.get(key) is not None]

    @validates_schema
    def validate_event_keys(self, data: dict[str, Any], **_: Any) -> dict[str, Any]:
        component_keys = self._get_component_keys(data)
        if not component_keys:
            raise (ValidationError(MISSING_COMPONENT_KEY))
        elif len(component_keys) > 1:
            raise ValidationError(f"{' and '.join(component_keys)} cannot be set at the same time.")
        elif component_keys[0] == "pipeline_key" and data["run_key"] is None:
            raise ValidationError(PIPELINE_EVENT_MISSING_REQUIRED_KEY)
        return data


class InstanceRefSchema(Schema):
    """Represent an instance with the corresponding journey"""

    journey = UUID(required=True)
    instance = UUID(required=True)

    @post_load
    def to_instance_ref(self, data: dict, **_: Any) -> InstanceRef:
        return InstanceRef(**data)


class EventSchema(EventApiSchema):
    """Represents the base-schema of an event message. Inherit from this to define your own event schema."""

    project_id = UUID(load_default=None, metadata={"description": "The project ID."})
    pipeline_id = UUID(load_default=None)
    dataset_id = UUID(load_default=None)
    server_id = UUID(load_default=None)
    stream_id = UUID(load_default=None)
    task_id = UUID(load_default=None)
    run_task_id = UUID(load_default=None)
    run_id = UUID(load_default=None)
    event_id = UUID(
        load_default=None,
        metadata={
            "description": (
                "A UUID identifying event. Legacy events will not be have an event_id and cannot be retrieved by ID."
            )
        },
    )
    received_timestamp = AwareDateTime(
        format="iso",
        required=True,
        default_timezone=UTC,
        metadata={"description": "An ISO timestamp that the Event Ingestion API applies when it receives the event."},
    )
    # This is the source of the message.
    source = EnumStr(
        dump_default=EventSources.UNKNOWN.name,
        load_default=EventSources.UNKNOWN.name,
        enum=EventSources,
    )
    # The event type. This is needed by an event-framework for deserializing, and it must be a string
    # matching the name of an Event-subclass.
    event_type = Str()

    instances = List(Nested(InstanceRefSchema), load_default=lambda: [])
    version = Enum(
        enum=EventVersion,
        load_default=EventVersion.V1,
        by_value=True,
    )
