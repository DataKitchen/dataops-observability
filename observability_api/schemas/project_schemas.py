__all__ = ["ProjectSchema", "ProjectPatchSchema"]

from marshmallow.fields import Pluck

from common.entities import Project

from .base_schemas import AuditEntitySchemaMixin, BaseEntitySchema
from .organization_schemas import OrganizationSchema


class ProjectSchema(BaseEntitySchema, AuditEntitySchemaMixin):
    organization = Pluck(OrganizationSchema, "id", dump_only=True)

    class Meta:
        model = Project


class ProjectPatchSchema(ProjectSchema):
    class Meta:
        fields = ("name", "description", "active")
