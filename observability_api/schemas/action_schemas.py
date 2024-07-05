__all__ = ["ApiActionSchema"]

from marshmallow.fields import Nested, Pluck

from common.entities import Action
from common.schemas.action_schemas import EmailActionArgsSchema, WebhookActionArgsSchema, ActionSchema
from .base_schemas import BaseEntitySchema
from .company_schemas import CompanySchema


class ApiActionSchema(BaseEntitySchema, ActionSchema):
    company = Pluck(CompanySchema, "id", dump_only=True)

    class Meta:
        model = Action


class SendEmailActionSchema(ApiActionSchema):
    action_args = Nested(EmailActionArgsSchema(), required=True)  # type: ignore[assignment]


class CallWebhookActionSchema(ApiActionSchema):
    action_args = Nested(WebhookActionArgsSchema(), required=True)  # type: ignore[assignment]
