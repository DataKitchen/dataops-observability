__all__ = [
    "BasePayload",
    "BasePayloadSchema",
    "EventResponseSchema",
    "EventV2",
]


from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from marshmallow import Schema
from marshmallow.fields import UUID, AwareDateTime, Dict, List, Str, Url

from common.constants import MAX_PAYLOAD_KEY_LENGTH
from common.schemas.validators import not_empty

from ...entities import EventEntity, InstanceSet
from ...entities.event import ApiEventType, EventVersion
from ..base import ComponentMixin, EventBaseMixin, JourneysMixin, ProjectMixin, RunMixin, TaskMixin
from ..event_handler import EventHandlerBase


@dataclass
class BasePayload:
    event_timestamp: Optional[datetime]
    metadata: dict[str, object]
    external_url: Optional[str]
    payload_keys: list[str]


class BasePayloadSchema(Schema):
    external_url = Url(
        load_default=None,
        metadata={"description": "A link to source information.", "example": "https://example.com"},
    )
    event_timestamp = AwareDateTime(
        load_default=None,
        format="iso",
        default_timezone=timezone.utc,
        metadata={
            "description": (
                "An ISO8601 timestamp that describes when the event occurred. "
                "If no timezone is specified, UTC is assumed."
            )
        },
    )
    metadata = Dict(
        load_default={},
        metadata={
            "description": "Arbitrary key-value information, supplied by the user, to apply to the event.",
            "example": {"external_id": "2f107d18-1e2f-40f1-acf7-16d0bdd13a04"},
        },
    )
    payload_keys = List(
        Str(validate=not_empty(max=MAX_PAYLOAD_KEY_LENGTH)),
        load_default=list,
        metadata={
            "description": "The key identifiers of the datums of interest.",
            "example": '["dataset-11", "dataset-59"]',
        },
    )


class EventResponseSchema(Schema):
    event_id = UUID()


@dataclass(kw_only=True)
class EventBase(EventBaseMixin, ProjectMixin, ComponentMixin, RunMixin, TaskMixin, JourneysMixin):
    event_payload: BasePayload

    def accept(self, handler: EventHandlerBase) -> bool:
        raise NotImplementedError


@dataclass(kw_only=True)
class EventV2(EventBase):
    event_type: ApiEventType = NotImplemented
    version: EventVersion = EventVersion.V2

    def to_event_entity(self) -> EventEntity:
        from .helpers import EVENT_TYPE_SCHEMAS

        instance_ids = [ir.instance for ir in self.instances]
        instance_set = InstanceSet.get_or_create(instance_ids) if instance_ids else None
        v2_schema = EVENT_TYPE_SCHEMAS[self.event_type]
        v2_payload = v2_schema().dump(self.event_payload)

        return EventEntity(
            id=self.event_id,
            version=self.version,
            type=self.event_type,
            created_timestamp=self.created_timestamp,
            timestamp=self.event_payload.event_timestamp,
            project=self.project_id,
            component=self.component_id,
            task=self.task_id,
            run=self.run_id,
            run_task=self.run_task_id,
            instance_set=instance_set,
            v2_payload=v2_payload,
        )
