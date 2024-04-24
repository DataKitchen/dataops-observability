__all__ = ["DatasetSchema"]

from common.entities.component import ComponentType
from common.schemas.fields import EnumStr
from observability_api.schemas import ComponentSchema


class DatasetSchema(ComponentSchema):
    type = EnumStr(
        enum=ComponentType,
        load_default=ComponentType.DATASET.value,
        dump_default=ComponentType.DATASET.value,
    )
