__all__ = ["OrganizationSchema", "OrganizationPatchSchema"]
from marshmallow.fields import Pluck

from common.entities import Organization

from .base_schemas import AuditEntitySchemaMixin, BaseEntitySchema
from .company_schemas import CompanySchema


class OrganizationSchema(BaseEntitySchema, AuditEntitySchemaMixin):
    company = Pluck(CompanySchema, "id", dump_only=True)

    class Meta:
        model = Organization


class OrganizationPatchSchema(OrganizationSchema):
    class Meta:
        fields = ("name", "description")
