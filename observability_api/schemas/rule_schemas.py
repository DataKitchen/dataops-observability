__all__ = [
    "RuleSchema",
    "RulePatchSchema",
    "RulePatchSendEmailSchema",
    "SendEmailRuleSchema",
    "CallWebhookRuleSchema",
    "RulePatchCallWebhookSchema",
]

from typing import Any

from marshmallow import ValidationError
from marshmallow.decorators import post_load, validates_schema
from marshmallow.fields import UUID, DateTime, Dict, Nested, Pluck

from common.entities import Rule
from common.predicate_engine.schemas.simple_v1 import RuleDataSchema
from common.schemas.fields import EnumStr
from observability_api.schemas import ComponentSchema, JourneySchema
from common.schemas.action_schemas import EmailActionArgsSchema, WebhookActionArgsSchema, ValidActions
from observability_api.schemas.base_schemas import BaseEntitySchema


class RuleSchema(BaseEntitySchema):
    created_on = DateTime(dump_only=True)
    component = (
        Pluck(
            ComponentSchema,
            "id",
            required=False,
            metadata={
                "description": "Optional. If an ID is specified, the rule will only apply to the specified component."
            },
        ),
    )
    # The contents or `rule_data` may not be JSON serializable, so for DB storage purposes, we keep the rule data
    # as a plain dict and manually validate it.
    rule_data = Dict(required=True, metadata={"description": "Required. The rule logic data."})
    journey = Pluck(JourneySchema, "id", dump_only=True, metadata={"description": "the parent Journey of the rule."})
    action = EnumStr(enum=ValidActions, required=True, metadata={"description": "Required. The type of the action."})
    action_args = Dict(
        required=True, metadata={"description": "Required. Arguments to be used in the Action execution."}
    )

    class Meta:
        model = Rule

    @post_load
    def load_action_args(self, data: dict, **_: Any) -> dict:
        if "action_args" in data:
            # We don't need to worry about KeyError here because this is a schema_validation. The EnumStr should
            # have already validated that the data exists.
            action_schema = ValidActions[data["action"]].value
            data["action_args"] = action_schema().load(data["action_args"])
        return data

    @validates_schema
    def validate_rule_data(self, data: dict, **_: object) -> None:
        try:
            RuleDataSchema().load(data["rule_data"])
        except ValidationError as e:
            raise ValidationError({"rule_data": str(e)})


class SendEmailRuleSchema(RuleSchema):
    action_args = Nested(EmailActionArgsSchema(), required=True)  # type: ignore[assignment]


class CallWebhookRuleSchema(RuleSchema):
    action_args = Nested(WebhookActionArgsSchema(), required=True)  # type: ignore[assignment]


class RulePatchSchema(BaseEntitySchema):
    # The contents or `rule_data` may not be JSON serializable, so for DB storage purposes, we keep the rule data
    # as a plain dict and manually validate it.
    rule_data = Dict(required=False, metadata={"description": "Required. The rule logic data."})
    action = EnumStr(enum=ValidActions, required=False, metadata={"description": "The name of the action."})
    action_args = Dict(required=False, metadata={"description": "The arguments to be used in the Action execution."})
    component = UUID(
        required=False,
        allow_none=True,
        metadata={
            "description": "Optional. If an ID is specified, the rule will only apply to the specified component."
        },
    )

    @validates_schema
    def validate_action_args(self, data: dict, **_: object) -> None:
        action_present = "action" in data
        action_args_present = "action_args" in data

        if action_present and not action_args_present:
            raise ValidationError({"action_args": "A change in action requires action_args."})
        if not action_present and action_args_present:
            raise ValidationError({"action": "A change in action_args requires an identifying action."})

    @post_load
    def load_action_args(self, data: dict, **_: Any) -> dict:
        if "action_args" in data:
            # We don't need to worry about KeyError here because this is a schema_validation. The EnumStr should
            # have already validated that the data exists.
            action_schema = ValidActions[data["action"]].value
            data["action_args"] = action_schema().load(data["action_args"])
        return data

    @validates_schema
    def validate_rule_data(self, data: dict, **_: object) -> None:
        if "rule_data" in data:
            try:
                RuleDataSchema().load(data["rule_data"])
            except ValidationError as e:
                raise ValidationError({"rule_data": str(e)})


class RulePatchSendEmailSchema(RulePatchSchema):
    action_args = Nested(EmailActionArgsSchema(), required=False)  # type: ignore[assignment]


class RulePatchCallWebhookSchema(RulePatchSchema):
    action_args = Nested(WebhookActionArgsSchema(), required=False)  # type: ignore[assignment]
