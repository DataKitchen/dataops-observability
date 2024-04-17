__all__ = ["InstanceRuleSchema", "InstanceRulePostSchema"]

from typing import Union

from marshmallow import Schema, ValidationError, pre_dump, validates_schema
from marshmallow.fields import UUID, Nested, Pluck

from common.constants import SCHEDULE_START_CRON_TIMEZONE
from common.entities import InstanceRule, InstanceRuleAction
from common.schemas.fields import CronExpressionStr, EnumStr, ZoneInfo
from observability_api.schemas.pipeline_schemas import PipelineSchema

from .base_schemas import BaseEntitySchema


class ScheduleInstanceRule(Schema):
    expression = CronExpressionStr(
        required=True,
        metadata={
            "description": (
                "Required. A cron expression that defines when the 'instance action' should occur. Does not support "
                "cron extensions. Recommended minimum no less than 10 minutes."
            ),
            "example": "15 * * * 1,3,5",
        },
    )
    timezone = ZoneInfo(
        load_default=SCHEDULE_START_CRON_TIMEZONE,
        metadata={
            "description": (
                "Optional. The local timezone of the expression defined by the schedule parameter, "
                "as an IANA long or short database name. "
                f"If unspecified, the schedule defaults to '{SCHEDULE_START_CRON_TIMEZONE}'."
            ),
            "example": "America/Sao_Paulo",
        },
    )


class InstanceRuleSchema(BaseEntitySchema):
    journey = Pluck(BaseEntitySchema, "id", dump_only=True)
    action = EnumStr(
        enum=InstanceRuleAction,
        required=True,
        metadata={"description": "Required. The selected action to perform when the rule's condition is satisfied."},
    )
    batch_pipeline = Pluck(PipelineSchema, "id", dump_only=True)
    schedule = Nested(ScheduleInstanceRule(), required=False, dump_default=None)

    @pre_dump(pass_many=True)
    def set_schedule_field(
        self, rules: Union[list[InstanceRule], InstanceRule], **_: dict
    ) -> Union[list[InstanceRule], InstanceRule]:
        for rule in rules if isinstance(rules, list) else [rules]:
            if (expression := rule.expression) is not None:
                rule.schedule = {"expression": expression, "timezone": rule.timezone}
        return rules


class InstanceRulePostSchema(Schema):
    action = EnumStr(
        enum=InstanceRuleAction,
        required=True,
        metadata={"description": "Required. The selected action to perform when the rule's condition is satisfied."},
    )
    batch_pipeline = UUID(required=False)
    schedule = Nested(ScheduleInstanceRule(), required=False)

    @validates_schema
    def validate_required_fields(self, data: dict, **_: object) -> None:
        pipeline_data = data.get("batch_pipeline", None)
        schedule_data = data.get("schedule", None)
        if bool(pipeline_data) is bool(schedule_data):
            raise ValidationError("Set exactly one of 'batch_pipeline' and 'schedule'")
