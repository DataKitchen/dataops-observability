__all__ = ["TestOutcome"]


from peewee import CharField, DecimalField, ForeignKeyField, TextField

from ..constants import (
    MAX_DESCRIPTION_LENGTH,
    MAX_TEST_OUTCOME_KEY_LENGTH,
    MAX_TEST_OUTCOME_NAME_LENGTH,
    MAX_TEST_OUTCOME_TYPE_LENGTH,
)
from ..peewee_extensions.fields import JSONStrListField, UTCTimestampField
from .base_entity import AuditUpdateTimeEntityMixin, BaseEntity
from .component import Component
from .instance import InstanceSet
from .run import Run
from .task import Task


class TestOutcome(BaseEntity, AuditUpdateTimeEntityMixin):
    """Represents a Test Outcome in the application."""

    component = ForeignKeyField(Component, null=False, backref="test_outcome_component", on_delete="CASCADE")
    description = CharField(null=True, max_length=MAX_DESCRIPTION_LENGTH)
    dimensions = JSONStrListField(null=False, column_name="dimension")
    end_time = UTCTimestampField(null=True, index=True)
    external_url = TextField(null=True)
    instance_set = ForeignKeyField(InstanceSet, null=True, backref="test_outcomes", on_delete="SET NULL")
    key = CharField(null=True, max_length=MAX_TEST_OUTCOME_KEY_LENGTH, index=True)
    metric_name = CharField(null=True, max_length=40)
    metric_description = CharField(null=True)
    max_threshold = DecimalField(null=True, max_digits=20, decimal_places=5)
    metric_value = DecimalField(null=True, max_digits=20, decimal_places=5)
    min_threshold = DecimalField(null=True, max_digits=20, decimal_places=5)
    name = CharField(null=False, max_length=MAX_TEST_OUTCOME_NAME_LENGTH)
    result = TextField(null=True)
    run = ForeignKeyField(Run, null=True, backref="test_outcome_run", on_delete="CASCADE")
    start_time = UTCTimestampField(null=True)
    status = CharField(null=False, index=True)
    task = ForeignKeyField(Task, null=True, backref="test_outcome_task", on_delete="CASCADE")
    type = CharField(null=True, max_length=MAX_TEST_OUTCOME_TYPE_LENGTH)

    class Meta:
        table_name = "test_outcome"
