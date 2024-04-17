__all__ = ["JourneyPatchSchema", "JourneySchema", "JourneyProjectSchema"]
from marshmallow.fields import Nested, Pluck, Str
from marshmallow_peewee import ModelSchema

from common.entities import Journey

from .base_schemas import AuditEntitySchemaMixin, BaseEntitySchema
from .project_schemas import ProjectSchema


class JourneyProjectSchema(BaseEntitySchema, AuditEntitySchemaMixin):
    project = Nested(ProjectSchema(only=["id", "name"]))

    class Meta:
        model = Journey


class JourneySchema(BaseEntitySchema, AuditEntitySchemaMixin):
    from .instance_rule_schemas import InstanceRuleSchema

    project = Pluck(ProjectSchema, "id", dump_only=True)
    instance_rules = Nested(InstanceRuleSchema, required=False, many=True, dump_only=True)

    class Meta:
        model = Journey


class JourneyPatchSchema(ModelSchema):
    name = Str(required=False, allow_none=True)
    description = Str(required=False, allow_none=True)
