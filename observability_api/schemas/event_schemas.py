__all__ = ["JourneyInstanceSchema", "EventResponseSchema"]

from typing import Any

from marshmallow import Schema
from marshmallow.fields import UUID, AwareDateTime, Dict, Enum, Nested
from marshmallow.utils import missing

from common.entities.event import ApiEventType, EventVersion
from observability_api.schemas.component_schemas import ComponentSchema
from observability_api.schemas.instance_schemas import InstanceSchema
from observability_api.schemas.journey_schemas import JourneySchema
from observability_api.schemas.project_schemas import ProjectSchema
from observability_api.schemas.run_schemas import RunSchema
from observability_api.schemas.task_schemas import RunTaskSchema, TaskSchema


class JourneyInstanceSchema(Schema):
    journey = Nested(JourneySchema, only=("id",), required=True)
    instance = Nested(InstanceSchema, only=("id",), required=True)


class EventResponseSchema(Schema):
    id = UUID(
        required=True,
        metadata={"description": "The event's unique ID"},
    )
    version = Enum(
        enum=EventVersion,
        dump_default=EventVersion.V1,
        by_value=True,
        metadata={"description": "The schema version of the event."},
    )
    event_type = Enum(
        enum=ApiEventType,
        by_value=True,
        attribute="type",
        metadata={"description": "The event's type"},
    )
    project = Nested(ProjectSchema, only=("id",), required=True)
    components = Nested(
        ComponentSchema,
        only=(
            "id",
            "type",
            "display_name",
            "tool",
            "testgen_components",
        ),
        many=True,
        dump_default=list,
        required=True,
        metadata={
            "description": (
                "The IDs of the components related to the event. The first item in the list is the primary component. "
            )
        },
    )
    run = Nested(RunSchema, only=("id",), dump_default={"id": None})
    task = Nested(TaskSchema, only=("id", "display_name"), dump_default={"id": None, "display_name": None})
    run_task = Nested(RunTaskSchema, only=("id",), dump_default={"id": None})
    timestamp = AwareDateTime()
    received_timestamp = AwareDateTime(attribute="created_timestamp")
    instances = Nested(
        JourneyInstanceSchema,
        many=True,
        dump_default=list,
        required=True,
        metadata={"description": "The IDs of the Instances the event belongs to."},
    )
    raw_data = Dict(
        attribute="v2_payload",
        required=True,
        metadata={"description": "The event data, as ingested."},
    )

    def get_attribute(self, obj: Any, attr: str, default: Any) -> Any:
        value = super().get_attribute(obj, attr, default)
        # "We return `missing` when some attributes are None to force marshmallow to apply the default value.
        return missing if value is None and attr in ("run", "task", "run_task") else value
