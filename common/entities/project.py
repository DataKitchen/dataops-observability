__all__ = ["Project"]

from peewee import CharField, ForeignKeyField

from .base_entity import ActivableEntityMixin, AuditEntityMixin, BaseEntity
from .organization import Organization


class Project(BaseEntity, ActivableEntityMixin, AuditEntityMixin):
    """Third (and currently final) tier of the organizational hierarchy"""

    name = CharField(null=False)
    description = CharField(null=True)
    organization = ForeignKeyField(Organization, backref="projects", on_delete="CASCADE", null=False, index=True)

    class Meta:
        indexes = ((("organization", "name"), True),)
