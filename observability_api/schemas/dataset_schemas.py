__all__ = ["DatasetSchema", "DatasetOperationsSummarySchema"]

from marshmallow import Schema
from marshmallow.fields import Int, Str

from common.entities.component import ComponentType
from common.events.v2 import DatasetOperationType
from common.schemas.fields import EnumStr
from observability_api.schemas import ComponentSchema


class DatasetSchema(ComponentSchema):
    type = EnumStr(
        enum=ComponentType,
        load_default=ComponentType.DATASET.value,
        dump_default=ComponentType.DATASET.value,
    )


class DatasetOperationsSummarySchema(Schema):
    operation = EnumStr(enum=DatasetOperationType, required=True)
    count = Int(required=True)
