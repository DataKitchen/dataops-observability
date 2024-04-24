__all__ = ["Rule", "RunState"]

from enum import Enum

from peewee import CharField, ForeignKeyField
from playhouse.mysql_ext import JSONField

from common.constants import MAX_ACTION_IMPL_LENGTH
from common.peewee_extensions.fields import UTCTimestampField

from .alert import RunAlertType
from .base_entity import AuditUpdateTimeEntityMixin, BaseEntity
from .component import Component
from .journey import Journey
from .run import RunStatus


class RunState(Enum):
    """Types of run states to match in the run state rule"""

    RUNNING = RunStatus.RUNNING.name
    COMPLETED = RunStatus.COMPLETED.name
    COMPLETED_WITH_WARNINGS = RunStatus.COMPLETED_WITH_WARNINGS.name
    FAILED = RunStatus.FAILED.name
    LATE_END = RunAlertType.LATE_END.name
    LATE_START = RunAlertType.LATE_START.name
    MISSING_RUN = RunAlertType.MISSING_RUN.name
    UNEXPECTED_STATUS_CHANGE = RunAlertType.UNEXPECTED_STATUS_CHANGE.name


class Rule(BaseEntity, AuditUpdateTimeEntityMixin):
    """Represents a rule to be processed by rules engine"""

    created_on = UTCTimestampField(null=False, defaults_to_now=True)
    component = ForeignKeyField(Component, backref="rules", on_delete="CASCADE", null=True, index=True)
    journey = ForeignKeyField(Journey, backref="rules", on_delete="CASCADE", null=False, index=True)
    rule_schema = CharField(null=False)
    rule_data = JSONField(null=False)
    action = CharField(null=False, max_length=MAX_ACTION_IMPL_LENGTH)
    action_args = JSONField(default=dict, null=False)
