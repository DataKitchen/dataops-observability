__all__ = ["AuditEntitySchemaMixin", "BaseEntitySchema"]
from marshmallow.fields import UUID, DateTime, Nested
from marshmallow_peewee import ModelSchema

from common.entities import BaseEntity, User


class BaseEntitySchema(ModelSchema):
    id = UUID(dump_only=True)

    class Meta:
        model = BaseEntity


class AuditUserSchema(BaseEntitySchema):
    class Meta:
        model = User
        fields = ("id", "name")


class AuditEntitySchemaMixin:
    created_on = DateTime(dump_only=True)
    created_by = Nested(AuditUserSchema(), dump_only=True)
