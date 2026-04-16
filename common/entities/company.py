__all__ = ["Company"]


from peewee import CharField, ForeignKeyField

from .base_entity import AuditEntityMixin, BaseEntity


class Company(BaseEntity, AuditEntityMixin):
    """Company is the top-level of the organizational hierarchy, representing an entire new Customer"""

    name = CharField(unique=True, null=False)

    @property
    def parent(self) -> ForeignKeyField | None:
        return None
