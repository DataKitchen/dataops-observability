__all__ = ["DatasetOperation", "DatasetOperationType"]

from enum import Enum

from peewee import CharField, ForeignKeyField

from common.constants import MAX_PATH_LENGTH
from common.peewee_extensions.fields import EnumStrField, UTCTimestampField

from .base_entity import BaseEntity
from .dataset import Dataset
from .instance import InstanceSet


class DatasetOperationType(Enum):
    READ = "READ"
    WRITE = "WRITE"


class DatasetOperation(BaseEntity):
    """Represents a Dataset Operation in the application."""

    dataset = ForeignKeyField(Dataset, backref="operations", on_delete="CASCADE")
    instance_set = ForeignKeyField(InstanceSet, null=True, backref="dataset_operations", on_delete="SET NULL")
    operation_time = UTCTimestampField(index=True)
    operation = EnumStrField(DatasetOperationType, max_length=10)
    path = CharField(null=True, max_length=MAX_PATH_LENGTH)

    class Meta:
        table_name = "dataset_operation"
