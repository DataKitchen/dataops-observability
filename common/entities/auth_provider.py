__all__ = ["AuthProvider"]
from peewee import CharField, ForeignKeyField

from common.peewee_extensions.fields import DomainField

from .base_entity import BaseEntity
from .company import Company


class AuthProvider(BaseEntity):
    """Authentication Provider Settings"""

    client_id = CharField(null=False)
    client_secret = CharField(null=False)
    company = ForeignKeyField(Company, backref="auth_providers", null=False, index=True)
    discovery_doc_url = CharField(null=False)
    domain = DomainField(null=False, unique=True, index=True)

    def __str__(self) -> str:
        return f"{self.domain} - #{self.company_id}"

    class Meta:
        table_name = "auth_provider"
