__all__ = [
    "LogEntry",
    "LogEntrySchema",
    "LogLevel",
    "MessageLog",
    "MessageLogSchema",
    "MessageLogUserEvent",
]

from dataclasses import dataclass
from enum import Enum as std_Enum
from typing import Any

from marshmallow import Schema, post_load
from marshmallow.fields import Enum, Nested, Str

from common.entities.event import ApiEventType
from common.events.event_handler import EventHandlerBase
from common.events.v2 import BasePayload, BasePayloadSchema, ComponentData, ComponentDataSchema
from common.events.v2.base import EventV2
from common.schemas.validators import not_empty


class LogLevel(std_Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class LogEntry:
    level: LogLevel
    message: str


@dataclass
class MessageLog(BasePayload):
    component: ComponentData
    log_entries: list[LogEntry]


class LogEntrySchema(Schema):
    level = Enum(
        required=True,
        enum=LogLevel,
        metadata={"description": "Required. The severity level of the message."},
    )
    message = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The body of the message to log.", "example": "The job has completed."},
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> LogEntry:
        return LogEntry(**data)


class MessageLogSchema(BasePayloadSchema):
    component = Nested(
        ComponentDataSchema,
        required=True,
        metadata={"description": "Required. The component associated to the log entries."},
    )
    log_entries = Nested(
        LogEntrySchema,
        required=True,
        validate=not_empty(),
        many=True,
        metadata={"description": "Optional. A list of log messages."},
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> MessageLog:
        return MessageLog(**data)


@dataclass(kw_only=True)
class MessageLogUserEvent(EventV2):
    event_payload: MessageLog
    event_type: ApiEventType = ApiEventType.MESSAGE_LOG

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_message_log_v2(self)
