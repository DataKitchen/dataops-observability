__all__ = ["EventEntity", "EventVersion", "ApiEventType"]

from enum import Enum, IntEnum

from peewee import ForeignKeyField, Node, fn
from playhouse.mysql_ext import JSONField

from common.peewee_extensions.fields import EnumIntField, EnumStrField, UTCTimestampField

from ..constants import MAX_EVENT_TYPE_LENGTH
from .base_entity import BaseEntity
from .component import Component
from .instance import InstanceSet
from .project import Project
from .run import Run
from .task import RunTask, Task


class EventVersion(IntEnum):
    V1 = 1
    V2 = 2


class ApiEventType(Enum):
    BATCH_PIPELINE_STATUS = "BATCH_PIPELINE_STATUS"
    DATASET_OPERATION = "DATASET_OPERATION"
    MESSAGE_LOG = "MESSAGE_LOG"
    METRIC_LOG = "METRIC_LOG"
    TEST_OUTCOMES = "TEST_OUTCOMES"


class EventEntity(BaseEntity):
    """An Observability Event."""

    version = EnumIntField(EventVersion)
    type = EnumStrField(ApiEventType, max_length=MAX_EVENT_TYPE_LENGTH)
    created_timestamp = UTCTimestampField(null=False, index=True)
    timestamp = UTCTimestampField(null=True, index=True)
    project = ForeignKeyField(Project, backref="events", on_delete="CASCADE", null=False)
    component = ForeignKeyField(Component, backref="events", on_delete="CASCADE", null=True)
    task = ForeignKeyField(Task, backref="events", on_delete="SET NULL", null=True)
    run = ForeignKeyField(Run, backref="events", on_delete="SET NULL", null=True)
    run_task = ForeignKeyField(RunTask, backref="events", on_delete="SET NULL", null=True)
    instance_set = ForeignKeyField(InstanceSet, null=True, backref="events", on_delete="SET NULL")
    v2_payload = JSONField(null=False)

    @classmethod
    def timestamp_coalesce(cls) -> Node:
        return fn.COALESCE(cls.timestamp, cls.created_timestamp)

    @property
    def components(self) -> list[Component]:
        return [self.component] if self.component else []
