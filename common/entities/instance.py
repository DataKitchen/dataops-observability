__all__ = ["Instance", "InstanceSet", "InstancesInstanceSets", "InstanceStatus", "InstanceStartType"]

import json
from enum import Enum
from typing import DefaultDict, Iterable, Union, cast
from uuid import UUID

from peewee import BooleanField, CharField, CompositeKey, Expression, ForeignKeyField, fn
from playhouse.hybrid import hybrid_property

from common.peewee_extensions.fields import EnumStrField, UTCTimestampField

from .base_entity import AuditUpdateTimeEntityMixin, BaseEntity, BaseModel
from .component import Component
from .journey import Journey, JourneyDagEdge


class InstanceStatus(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"

    @staticmethod
    def as_set() -> set[str]:
        return {s.name for s in InstanceStatus}


class InstanceStartType(Enum):
    BATCH = "BATCH"
    SCHEDULED = "SCHEDULED"
    DEFAULT = "DEFAULT"
    PAYLOAD = "PAYLOAD"


class Instance(BaseEntity, AuditUpdateTimeEntityMixin):
    """Represents a single instance of a Journey."""

    journey = ForeignKeyField(Journey, null=False, backref="instances", on_delete="CASCADE")
    start_time = UTCTimestampField(null=False, defaults_to_now=True)
    end_time = UTCTimestampField(null=True, index=True)
    has_errors = BooleanField(default=False)
    has_warnings = BooleanField(default=False)
    payload_key = CharField(null=True)
    start_type = EnumStrField(InstanceStartType, default=InstanceStartType.DEFAULT, null=False, max_length=50)

    @hybrid_property  # type: ignore [misc]
    def active(self) -> Union[Expression, bool]:
        return self.end_time == None

    @property
    def status(self) -> str:
        if self.has_errors:
            return InstanceStatus.ERROR.value
        elif self.has_warnings:
            return InstanceStatus.WARNING.value
        elif self.active:
            return InstanceStatus.ACTIVE.value
        else:
            return InstanceStatus.COMPLETED.value

    @property
    def journey_dag(self) -> DefaultDict[Component, set[JourneyDagEdge]]:
        """Return a graph of Components taken from the Journey."""
        return cast(DefaultDict[Component, set[JourneyDagEdge]], self.journey.journey_dag)

    @property
    def dag_nodes(self) -> list[Component]:
        return cast(list[Component], self.journey.dag_nodes)

    @staticmethod
    def make_status_filter(statuses: list[str]) -> list:
        memberships = []
        if InstanceStatus.ERROR in statuses:
            memberships.append(Instance.has_errors == True)
        if InstanceStatus.WARNING in statuses:
            memberships.append((Instance.has_warnings == True) & (Instance.has_errors == False))
        if InstanceStatus.ACTIVE in statuses:
            memberships.append(
                (Instance.has_warnings == False) & (Instance.has_errors == False) & Instance.end_time.is_null()
            )
        if InstanceStatus.COMPLETED in statuses:
            memberships.append(
                (Instance.has_warnings == False) & (Instance.has_errors == False) & Instance.end_time.is_null(False)
            )
        return memberships


class InstanceSet(BaseEntity, AuditUpdateTimeEntityMixin):
    """
    Represents a set of Instances.

    It is used to replace multiple Many-To-Many relationship tables by concentrating
    a set of Instances under an single entity that can be referenced by a Foreign Key.
    """

    class Meta:
        table_name = "instance_set"

    @classmethod
    def get_or_create(cls, instance_ids: Iterable[UUID]) -> "InstanceSet":
        if not instance_ids:
            raise ValueError("An InstanceSet can not be empty.")

        instance_ids_json_array = fn.JSON_ARRAYAGG(InstancesInstanceSets.instance).alias("id_array")
        instance_ids_json_value = json.dumps([i_id.hex for i_id in instance_ids])

        iis_inner = InstancesInstanceSets.alias("inner")
        iis_inner_query = iis_inner.select(iis_inner.instance_set).distinct().where(iis_inner.instance << instance_ids)

        iis_query = (
            InstancesInstanceSets.select(InstancesInstanceSets.instance_set, InstanceSet, instance_ids_json_array)
            .left_outer_join(InstanceSet)
            .where(InstancesInstanceSets.instance_set << iis_inner_query)
            .group_by(cls.id, InstancesInstanceSets.instance_set)
            .having(
                fn.JSON_CONTAINS(instance_ids_json_array, instance_ids_json_value)
                & fn.JSON_CONTAINS(instance_ids_json_value, instance_ids_json_array)
            )
        )

        try:
            return cast(InstanceSet, iis_query.get().instance_set)
        except InstancesInstanceSets.DoesNotExist:
            pass

        new_instance_set: InstanceSet = cls.create()
        InstancesInstanceSets.bulk_create(
            [
                InstancesInstanceSets(instance_set=new_instance_set.id, instance=instance_id)
                for instance_id in instance_ids
            ]
        )
        return new_instance_set


class InstancesInstanceSets(BaseModel, AuditUpdateTimeEntityMixin):
    """Join table. Represents a link between Instances and InstanceSets."""

    instance = ForeignKeyField(Instance, backref="iis", on_delete="CASCADE")
    instance_set = ForeignKeyField(InstanceSet, backref="iis", on_delete="CASCADE")

    class Meta:
        table_name = "instances_instancesets"
        primary_key = CompositeKey("instance", "instance_set")
