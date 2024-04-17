__all__ = ["MessageLogEventSchema", "MessageLogEventApiSchema", "MessageLogEvent", "MessageEventLogLevel"]

from dataclasses import dataclass
from enum import Enum

from marshmallow import Schema
from marshmallow.fields import Str

from common.events.event_handler import EventHandlerBase
from common.events.v1.event import Event
from common.events.v1.event_schemas import EventApiSchema, EventSchema
from common.schemas.fields import EnumStr
from common.schemas.validators import not_empty


class MessageEventLogLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class MessageLogEventBaseSchema(Schema):
    log_level = EnumStr(
        required=True,
        enum=MessageEventLogLevel,
        metadata={"description": "Required. The severity level of the message."},
    )
    message = Str(
        required=True,
        validate=not_empty(),
        metadata={"description": "Required. The body of the message to log.", "example": "The job has completed."},
    )


class MessageLogEventSchema(MessageLogEventBaseSchema, EventSchema):
    pass


class MessageLogEventApiSchema(MessageLogEventBaseSchema, EventApiSchema):
    pass


@dataclass
class MessageLogEvent(Event):
    """Represents a log message related to the pipeline, and optionally related to a specific task."""

    log_level: str
    message: str

    __schema__ = MessageLogEventSchema
    __api_schema__ = MessageLogEventApiSchema

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_message_log(self)
