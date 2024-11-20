__all__ = ["Component", "ComponentType"]

from enum import Enum
from typing import cast

from peewee import CharField, ForeignKeyField
from playhouse.mysql_ext import JSONField

from .base_entity import AuditEntityMixin, AuditUpdateTimeEntityMixin, BaseEntity
from .project import Project


class ComponentType(Enum):
    BATCH_PIPELINE = "BATCH_PIPELINE"
    STREAMING_PIPELINE = "STREAMING_PIPELINE"
    DATASET = "DATASET"
    SERVER = "SERVER"


class Component(BaseEntity, AuditEntityMixin, AuditUpdateTimeEntityMixin):
    """
    Representation of a Component in the application.

    Component sub-types should be created using the ComponentMeta metaclass instead of inheriting form this class.
    """

    key = CharField(unique=False, null=False)
    name = CharField(unique=False, null=True)
    description = CharField(null=True)
    labels = JSONField(default=None, null=True)
    project = ForeignKeyField(Project, backref="components", on_delete="CASCADE", null=False, index=True)
    type = CharField(null=False, max_length=40)
    tool = CharField(null=True)

    class Meta:
        indexes = (
            (("project_id", "key", "type"), True),  # project & key & type must be unique together
            (("project_id", "key"), False),  # keep project & key indexed without type to allow fast lookups
        )

    @property
    def display_name(self) -> str:
        """Returns the value to be displayed in a user interface. Uses name if set, falls back to key."""
        value: str = self.name if self.name else self.key
        return value

    @property
    def display_type(self) -> str:
        """Returns the display value for the component type."""
        return " ".join(word.capitalize() for word in cast(str, self.type).split("_"))

    @property
    def type_instance(self) -> BaseEntity:
        """
        Returns an instance of the specific component.

        This method utilizes the `_get_<component_type>_instance` methods created by the ComponentMeta metaclass
        """
        instance: BaseEntity = getattr(self, f"_get_{self.type.lower()}_instance")()
        return instance
