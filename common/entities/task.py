from __future__ import annotations

__all__ = ["Task", "RunTask", "RunTaskStatus"]

from enum import IntEnum

from peewee import BooleanField, CharField, ForeignKeyField, TextField

from common.peewee_extensions.fields import UTCTimestampField

from .base_entity import BaseEntity
from .pipeline import Pipeline
from .run import Run


class RunTaskStatus(IntEnum):
    # The int values must be higher the more severe the status is for max() to
    # work
    PENDING = 1
    MISSING = 2
    RUNNING = 3
    COMPLETED = 4
    COMPLETED_WITH_WARNINGS = 5
    FAILED = 6

    @staticmethod
    def max(left: str, right: str) -> RunTaskStatus:
        """Return the most critical type i.e. the maximum criticality"""
        try:
            enums = [RunTaskStatus[t] for t in (left, right)]
        except KeyError as e:
            raise ValueError(f"{e} is not a valid RunTaskStatus")

        return max(enums)

    @staticmethod
    def as_set() -> set[str]:
        return {s.name for s in RunTaskStatus}


class Task(BaseEntity):
    """Represents a task within a Pipeline."""

    key = CharField(unique=False, null=False)
    name = CharField(unique=False, null=True)
    description = TextField(null=False, default="")
    required = BooleanField(default=False, null=False)
    pipeline = ForeignKeyField(Pipeline, backref="pipeline_tasks", on_delete="CASCADE", null=False, index=True)

    class Meta:
        indexes = ((("key", "pipeline"), True),)  # task key must be unique in pipeline

    @property
    def display_name(self) -> str:
        """Returns the value to be displayed in a user interface. Uses name if set, falls back to key."""
        value: str = self.name if self.name else self.key
        return value


class RunTask(BaseEntity):
    """Represents a single instance of a pipeline task execution."""

    required = BooleanField(default=False, null=False)
    status = CharField(default=RunTaskStatus.PENDING.name, null=False)
    start_time = UTCTimestampField(null=True)
    end_time = UTCTimestampField(null=True)
    run = ForeignKeyField(Run, backref="run_tasks", on_delete="CASCADE", null=False, index=True)
    task = ForeignKeyField(Task, backref="run_tasks", on_delete="CASCADE", null=False, index=True)

    class Meta:
        table_name = "run_task"
        indexes = ((("run", "task"), True),)  # only one RunTask per run and task
