__all__ = ["ServerSchema"]

from common.entities.component import ComponentType
from common.schemas.fields import EnumStr
from observability_api.schemas import ComponentSchema


class ServerSchema(ComponentSchema):
    type = EnumStr(
        enum=ComponentType,
        load_default=ComponentType.SERVER.value,
        dump_default=ComponentType.SERVER.value,
    )
