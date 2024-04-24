__all__ = ["Run", "RunStatus", "FINISHED_RUN_STATUSES", "END_RUN_STATUSES"]

from enum import Enum

from peewee import CharField, Check, ForeignKeyField

from common.constants import MAX_RUN_NAME_LENGTH
from common.peewee_extensions.fields import UTCTimestampField

from .base_entity import AuditUpdateTimeEntityMixin, BaseEntity
from .instance import InstanceSet
from .pipeline import Pipeline


class RunStatus(Enum):
    PENDING = "PENDING"
    MISSING = "MISSING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"

    @staticmethod
    def is_end_status(run_status: str) -> bool:
        return run_status in (
            RunStatus.MISSING.name,
            RunStatus.COMPLETED.name,
            RunStatus.COMPLETED_WITH_WARNINGS.name,
            RunStatus.FAILED.name,
        )

    @staticmethod
    def has_run_started(run_status: str) -> bool:
        return run_status not in (RunStatus.MISSING.name, RunStatus.PENDING.name)


FINISHED_RUN_STATUSES = (RunStatus.COMPLETED.name, RunStatus.COMPLETED_WITH_WARNINGS.name, RunStatus.FAILED.name)
"""Finished run statuses. I.e. statuses for runs that executed and finished with a status."""
END_RUN_STATUSES = (
    *FINISHED_RUN_STATUSES,
    RunStatus.MISSING.name,
)
"""End run statuses. I.e. statuses for runs that are not expected to receive a new status."""


class Run(BaseEntity, AuditUpdateTimeEntityMixin):
    """Represents a single instance of a pipeline execution."""

    key = CharField(null=True, index=True)
    name = CharField(max_length=MAX_RUN_NAME_LENGTH, null=True)
    start_time = UTCTimestampField(null=True, defaults_to_now=True, index=True)
    end_time = UTCTimestampField(null=True, index=True)
    expected_start_time = UTCTimestampField(null=True)
    expected_end_time = UTCTimestampField(null=True)
    pipeline = ForeignKeyField(Pipeline, null=False, backref="pipeline_runs", on_delete="CASCADE")
    instance_set = ForeignKeyField(InstanceSet, null=True, backref="runs", on_delete="SET NULL")
    status = CharField(index=True)

    class Meta:
        indexes = ((("pipeline", "key"), True),)
        constraints = [
            Check(
                "(`start_time` IS NULL AND `status` IN ('PENDING', 'MISSING')) OR "
                "(`start_time` IS NOT NULL AND `status` NOT IN ('PENDING', 'MISSING'))",
                "run_start_time_set",
            ),
            Check(
                "(`key` IS NULL AND `status` IN ('PENDING', 'MISSING')) OR "
                "(`key` IS NOT NULL AND `status` NOT IN ('PENDING', 'MISSING'))",
                "run_key_set",
            ),
        ]
