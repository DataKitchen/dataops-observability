__all__ = ["ActivableEntityMixin", "AuditEntityMixin", "AuditUpdateTimeEntityMixin", "BaseEntity", "BaseModel", "DB"]

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from peewee import BooleanField, DatabaseProxy, DeferredForeignKey, Model, UUIDField

from common.peewee_extensions.fields import UTCTimestampField

DB = DatabaseProxy()
"""Proxy to defer database initialization."""


class BaseModel(Model):
    """Base class for models stored in SQL."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}#{self.id}"

    @property
    def module_path(self) -> str:
        return f"{self.__module__}.{self.__name__}"

    class Meta:
        only_save_dirty = True
        database = DB


class BaseEntity(BaseModel):
    """Base class for entities stored in SQL."""

    id = UUIDField(primary_key=True, null=False, index=True, unique=True, default=uuid4)


class AuditEntityMixin(Model):
    """Mixin class for all entities that we want to track who created and when."""

    created_on = UTCTimestampField(null=False, defaults_to_now=True)
    created_by = DeferredForeignKey("User", null=True, on_delete="SET NULL")


class ActivableEntityMixin(Model):
    """Mixin class for all entities that can be [de]activated."""

    active = BooleanField(default=True, null=False)


class AuditUpdateTimeEntityMixin(Model):
    """Mixin class for all entities that we want to track the last updated time."""

    updated_on = UTCTimestampField(null=False, defaults_to_now=True)

    @classmethod
    def update(cls, *args: Any, **kwargs: Any) -> Any:
        kwargs["updated_on"] = datetime.utcnow().replace(tzinfo=UTC)
        return super().update(*args, **kwargs)
