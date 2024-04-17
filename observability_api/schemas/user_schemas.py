__all__ = ["UserSchema", "UserPatchSchema"]

from marshmallow.fields import Pluck, Str

from .base_schemas import AuditEntitySchemaMixin, BaseEntitySchema
from .company_schemas import CompanySchema


class UserSchema(BaseEntitySchema, AuditEntitySchemaMixin):
    primary_company = Pluck(CompanySchema, "id", dump_only=True)
    name = Str(required=True)
    email = Str(required=True)
    username = Str(required=False)


class UserPatchSchema(UserSchema):
    class Meta:
        # excluded email and foreign_user_id; cannot be changed after creation!
        fields = ("name", "admin", "active")
