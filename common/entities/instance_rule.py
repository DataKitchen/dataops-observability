__all__ = ["InstanceRuleAction", "InstanceRule"]

from enum import Enum

from peewee import CharField, Check, ForeignKeyField

from common.constants.schema_limits import MAX_CRON_EXPRESSION_LENGTH, MAX_TIMEZONE_LENGTH
from common.peewee_extensions.fields import EnumStrField, ZoneInfoField

from .base_entity import AuditUpdateTimeEntityMixin, BaseEntity
from .component import Component
from .journey import Journey


class InstanceRuleAction(Enum):
    START = "START"
    END = "END"
    END_PAYLOAD = "END_PAYLOAD"


class InstanceRule(BaseEntity, AuditUpdateTimeEntityMixin):
    journey = ForeignKeyField(Journey, null=False, backref="instance_rules", on_delete="CASCADE")
    action = EnumStrField(InstanceRuleAction, null=False)
    batch_pipeline = ForeignKeyField(Component, null=True, backref="instance_rules", on_delete="CASCADE")
    expression = CharField(max_length=MAX_CRON_EXPRESSION_LENGTH, null=True)
    timezone = ZoneInfoField(max_length=MAX_TIMEZONE_LENGTH, null=True)

    class Meta:
        table_name = "instances_rules"
        constraints = [
            Check(
                "(`batch_pipeline_id` IS NOT NULL AND `expression` IS NULL) OR "
                "(`batch_pipeline_id` IS NULL AND `expression` IS NOT NULL)",
                "component_xor_schedule",
            )
        ]
