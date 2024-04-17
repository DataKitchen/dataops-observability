__all__ = ["Schedule", "ScheduleExpectation"]

from enum import Enum

from peewee import CharField, ForeignKeyField, IntegerField

from common.peewee_extensions.fields import ZoneInfoField

from ..constants import MAX_CRON_EXPRESSION_LENGTH, MAX_TIMEZONE_LENGTH
from .base_entity import AuditEntityMixin, AuditUpdateTimeEntityMixin, BaseEntity
from .component import Component


class ScheduleExpectation(Enum):
    """Valid values for the Schedule expectation."""

    BATCH_PIPELINE_START_TIME = "BATCH_PIPELINE_START_TIME"
    BATCH_PIPELINE_END_TIME = "BATCH_PIPELINE_END_TIME"
    DATASET_ARRIVAL = "DATASET_ARRIVAL"


class Schedule(BaseEntity, AuditEntityMixin, AuditUpdateTimeEntityMixin):
    """Schedule that sets the time-based expectations for a given BatchPipeline."""

    component = ForeignKeyField(Component, backref="schedules", on_delete="CASCADE")
    description = CharField(max_length=300, null=True)
    schedule = CharField(max_length=MAX_CRON_EXPRESSION_LENGTH)
    timezone = ZoneInfoField(max_length=MAX_TIMEZONE_LENGTH)
    expectation = CharField(max_length=50)
    margin = IntegerField(null=True)

    class Meta:
        indexes = ((("component", "expectation"), True),)
