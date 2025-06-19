__all__ = ["ApiKey", "Service", "ServiceAccountKey"]
import logging
from datetime import datetime, UTC
from enum import Enum
from uuid import uuid4

from peewee import BlobField, CharField, ForeignKeyField, Model, UUIDField

from common.entities.base_entity import DB
from common.peewee_extensions.fields import JSONStrListField, UTCTimestampField

from .project import Project
from .user import User

LOG = logging.getLogger(__name__)


class ApiKey(Model):
    """An API key for authentication."""

    id = UUIDField(primary_key=True, null=False, index=True, unique=True, default=uuid4)
    digest = BlobField(null=False)
    expiry = UTCTimestampField(null=False)
    user = ForeignKeyField(User, backref="api_keys", on_delete="CASCADE", null=False, index=True)

    def is_expired(self) -> bool:
        if datetime.now(UTC) > self.expiry:
            return True
        else:
            return False

    def __str__(self) -> str:
        return f"{self.__class__.__name__}#{self.id}"

    class Meta:
        only_save_dirty = True
        database = DB
        table_name = "api_key"


class Service(Enum):
    EVENTS_API = "EVENTS_API"
    OBSERVABILITY_API = "OBSERVABILITY_API"
    AGENT_API = "AGENT_API"


class ServiceAccountKey(Model):
    """An authentication key that is not tied to a specific user."""

    id = UUIDField(primary_key=True, null=False, index=True, unique=True, default=uuid4)
    description = CharField(null=True)
    digest = BlobField(null=False)
    expiry = UTCTimestampField(null=False)
    name = CharField(null=False)
    project = ForeignKeyField(Project, backref="service_account_keys", on_delete="CASCADE", null=False, index=True)
    allowed_services = JSONStrListField(null=False)

    def is_expired(self) -> bool:
        # If no expiration date is set, the key's duration is unlimited
        if not self.expiry:
            return False
        if datetime.now(UTC) > self.expiry:
            return True
        else:
            return False

    def __str__(self) -> str:
        return f"{self.allowed_services} Account Key: #{self.id}"

    class Meta:
        only_save_dirty = True
        database = DB
        table_name = "service_account_key"
        indexes = ((("name", "project"), True),)  # Name must be unique to the user
