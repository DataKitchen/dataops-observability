__all__ = ("HeartbeatSchema",)

from marshmallow import Schema
from marshmallow.fields import AwareDateTime, String
from marshmallow.validate import Length


class HeartbeatSchema(Schema):
    key = String(required=True, validate=Length(max=255))
    tool = String(required=True, validate=Length(max=255))
    version = String(required=True, validate=Length(max=255))
    latest_event_timestamp = AwareDateTime(format="iso", load_default=None, dump_default=None)
