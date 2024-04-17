__all__ = ["ServiceAccountKeySchema", "ServiceAccountKeyCreateSchema", "ServiceAccountKeyTokenSchema"]

from marshmallow import Schema, pre_dump
from marshmallow.fields import DateTime, Enum, Int, List, Pluck, Str
from marshmallow.validate import Length

from common.auth.keys.service_key import KeyPair
from common.constants import MAX_SERVICE_ACCOUNT_KEY_DESCRIPTION_LENGTH, MAX_SERVICE_ACCOUNT_KEY_NAME_LENGTH
from common.entities.authentication import Service
from common.schemas.fields import EnumStr
from common.schemas.validators import not_empty
from observability_api.schemas import BaseEntitySchema, ProjectSchema


class ServiceAccountKeySchema(BaseEntitySchema):
    expires_at = DateTime(required=True, dump_only=True, attribute="expiry")
    name = Str(required=True, dump_only=True)
    description = Str(required=False, allow_none=True, dump_only=True)
    project = Pluck(ProjectSchema, "id", dump_only=True)
    allowed_services = List(EnumStr(Service), required=True, validate=not_empty(), dump_only=True)


class ServiceAccountKeyTokenSchema(ServiceAccountKeySchema):
    token = Str(required=True)

    @pre_dump
    def parse_args(self, item: KeyPair, **_: object) -> object:
        item.key_entity.token = item.encoded_key
        return item.key_entity


class ServiceAccountKeyCreateSchema(Schema):
    project = Pluck(ProjectSchema, "id", dump_only=True)
    name = Str(required=True, validate=not_empty(max=MAX_SERVICE_ACCOUNT_KEY_NAME_LENGTH))
    description = Str(required=False, allow_none=True, validate=Length(max=MAX_SERVICE_ACCOUNT_KEY_DESCRIPTION_LENGTH))
    expires_after_days = Int(required=True)
    allowed_services = List(
        Enum(Service),
        required=True,
        metadata={"description": "Required.  Services for which the key will be valid."},
        validate=not_empty(),
    )
