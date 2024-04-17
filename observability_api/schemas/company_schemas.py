__all__ = ["CompanySchema", "CompanyPatchSchema"]

from common.entities import Company

from .base_schemas import AuditEntitySchemaMixin, BaseEntitySchema


class CompanySchema(BaseEntitySchema, AuditEntitySchemaMixin):
    class Meta:
        model = Company


class CompanyPatchSchema(CompanySchema):
    class Meta:
        fields = ("name",)
