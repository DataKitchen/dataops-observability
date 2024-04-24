__all__ = ["RunAlert", "InstanceAlert", "AlertLevel", "InstanceAlertsComponents", "InstanceAlertType", "RunAlertType"]

from datetime import datetime
from enum import Enum
from typing import Optional

from peewee import CharField, CompositeKey, ForeignKeyField
from playhouse.mysql_ext import JSONField

from common.constants.schema_limits import MAX_DESCRIPTION_LENGTH
from common.datetime_utils import datetime_to_timestamp, timestamp_to_datetime
from common.peewee_extensions.fields import EnumStrField, UTCTimestampField

from .base_entity import AuditUpdateTimeEntityMixin, BaseEntity, BaseModel
from .component import Component
from .instance import Instance
from .run import Run


class AlertLevel(Enum):
    """Valid alert levels"""

    WARNING = "WARNING"
    ERROR = "ERROR"


class RunAlertType(Enum):
    """Valid run alert types"""

    LATE_END = "LATE_END"
    LATE_START = "LATE_START"
    MISSING_RUN = "MISSING_RUN"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"
    UNEXPECTED_STATUS_CHANGE = "UNEXPECTED_STATUS_CHANGE"

    @staticmethod
    def as_set() -> set[str]:
        return {s.name for s in RunAlertType}


class InstanceAlertType(Enum):
    LATE_END = "LATE_END"
    LATE_START = "LATE_START"
    INCOMPLETE = "INCOMPLETE"
    OUT_OF_SEQUENCE = "OUT_OF_SEQUENCE"
    DATASET_NOT_READY = "DATASET_NOT_READY"
    TESTS_FAILED = "TESTS_FAILED"
    TESTS_HAD_WARNINGS = "TESTS_HAD_WARNINGS"

    @staticmethod
    def as_set() -> set[str]:
        return {s.name for s in InstanceAlertType}


class AlertBase(BaseEntity, AuditUpdateTimeEntityMixin):
    """Base class for Alerts."""

    created_on = UTCTimestampField(null=False, defaults_to_now=True)
    name = CharField(unique=False, null=True)
    details = JSONField(default=dict, null=False)
    description = CharField(null=False, max_length=MAX_DESCRIPTION_LENGTH)
    level = EnumStrField(AlertLevel, null=False, max_length=50)

    @property
    def expected_start_time(self) -> Optional[datetime]:
        """If the alert has expected_start_time in it's details dict, return it as a datetime object."""
        timestamp = self.details.get("expected_start_time", None)
        if timestamp:
            try:
                dt_obj = timestamp_to_datetime(timestamp)
            except Exception as e:
                raise ValueError(f"Invalid expected_start_time value `{timestamp}`") from e
            return dt_obj
        else:
            return None

    @expected_start_time.setter
    def expected_start_time(self, dt_obj: Optional[datetime]) -> None:
        """Set the expected_start_time value (converts to timestamp in details dict)."""
        if dt_obj is None:
            self.details.pop("expected_start_time", None)
        else:
            timestamp = datetime_to_timestamp(dt_obj)
            self.details["expected_start_time"] = timestamp

    @property
    def expected_end_time(self) -> Optional[datetime]:
        """If the alert has expected_end_time in it's details dict, return it as a datetime object."""
        timestamp = self.details.get("expected_end_time", None)
        if timestamp:
            try:
                dt_obj = timestamp_to_datetime(timestamp)
            except Exception as e:
                raise ValueError(f"Invalid expected_end_time value `{timestamp}`") from e
            return dt_obj
        else:
            return None

    @expected_end_time.setter
    def expected_end_time(self, dt_obj: Optional[datetime]) -> None:
        """Set the expected_end_time value (converts to timestamp in details dict)."""
        if dt_obj is None:
            self.details.pop("expected_end_time", None)
        else:
            timestamp = datetime_to_timestamp(dt_obj)
            self.details["expected_end_time"] = timestamp


class InstanceAlert(AlertBase):
    type = EnumStrField(InstanceAlertType, null=False, max_length=100)
    instance = ForeignKeyField(Instance, backref="instance_alerts", on_delete="CASCADE", null=False)

    class Meta:
        table_name = "instance_alerts"


class RunAlert(AlertBase):
    type = EnumStrField(RunAlertType, null=False, max_length=100)
    run = ForeignKeyField(Run, backref="run_alerts", on_delete="CASCADE", null=False)

    class Meta:
        table_name = "run_alerts"


class InstanceAlertsComponents(BaseModel):
    """Join table. Represents a link between InstanceAlert and Component."""

    instance_alert = ForeignKeyField(InstanceAlert, backref="iac", on_delete="CASCADE")
    component = ForeignKeyField(Component, backref="iac", on_delete="CASCADE")

    class Meta:
        table_name = "instance_alerts_components"
        primary_key = CompositeKey("instance_alert", "component")
