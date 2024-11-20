from enum import IntEnum, Enum

from marshmallow import Schema, post_load, post_dump
from marshmallow.fields import Str, Int, List, Email, Nested, Url, Dict, UUID
from marshmallow.validate import Length

from common.schemas.fields import EnumStr
from common.schemas.validators import not_empty


class SMTPConfigSchema(Schema):
    endpoint = Str(required=True)
    port = Int(required=True)
    username = Str(required=True)
    password = Str(required=True, load_only=True)


class EmailActionArgsSchema(Schema):
    from_address = Str(required=False, validate=not_empty(max=255))
    template = Str(validate=not_empty(max=255))
    recipients = List(Email(), required=True, validate=Length(max=50))
    smtp_config = Nested(SMTPConfigSchema(), required=False)


class HttpMethod(IntEnum):
    """This is a list of supported HTTP methods when calling a webhook."""

    DELETE = 1
    GET = 2
    PATCH = 3
    POST = 4
    PUT = 5


class WebhookActionHeader(Schema):
    """A HTTP header where "key" is the header name and "value" its value."""

    key = Str(
        validate=not_empty(),
        required=True,
        metadata={
            "description": "The header name.",
        },
    )
    value = Str(
        required=True,
        metadata={
            "description": "The header value.",
        },
    )


class WebhookActionArgsSchema(Schema):
    url = Url(
        required=True,
        schemes={"http", "https"},
        metadata={
            "description": "The webhook URL to call.",
            "example": "https://example.com/webhook/B529NCKCMCC",
        },
    )
    method = EnumStr(
        enum=HttpMethod,
        required=False,
        load_default=HttpMethod.POST.name,
        metadata={
            "description": "The HTTP method to use in the webhook call.",
            "example": "POST",
        },
    )
    payload = Dict(
        required=False,
        load_default=None,
        metadata={
            "description": "The payload to attach to the webhook call.",
            "example": {"message": "Pipeline {pipeline.name} has status {run.status}"},
        },
    )
    headers = List(
        Nested(WebhookActionHeader()),
        required=False,
        load_default=None,
        metadata={
            "description": "The headers to set in the webhook call.",
            "example": [{"key": "ID", "value": "829709080"}],
        },
    )


class ValidActions(Enum):
    """
    The list of valid actions. The enumeration is expected to be the valid schema for decoding this data.
    """

    SEND_EMAIL = EmailActionArgsSchema
    CALL_WEBHOOK = WebhookActionArgsSchema


class ActionSchema(Schema):
    id = UUID(dump_only=True)
    action_impl = EnumStr(enum=ValidActions, required=True, metadata={"description": "The name of the action."})
    action_args = Dict(required=False)

    @post_load
    def load_action_args(self, data: dict, **kwargs: dict) -> dict:
        if "action_args" in data:
            action_schema = ValidActions[data["action_impl"]].value
            data["action_args"] = action_schema().load(data["action_args"])
        return data

    @post_dump
    def dump_action_args(self, data: dict, **kwargs: dict) -> dict:
        if "action_args" in data:
            action_schema = ValidActions[data["action_impl"]].value
            data["action_args"] = action_schema().dump(data["action_args"])
        return data
