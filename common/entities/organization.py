__all__ = ["Organization"]

from peewee import CharField, ForeignKeyField

from .base_entity import AuditEntityMixin, BaseEntity
from .company import Company


class Organization(BaseEntity, AuditEntityMixin):
    """Second tier of hierarchy -- representing a subsection of the Company"""

    name = CharField(null=False)
    description = CharField(null=True)
    company = ForeignKeyField(Company, backref="organizations", on_delete="CASCADE", null=False, index=True)

    class Meta:
        # Multi-column indexes
        indexes = (
            # Unique index across company + name
            (("company", "name"), True),
        )
