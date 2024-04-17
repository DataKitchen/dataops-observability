__all__ = ["PipelineSchema"]

from common.entities.component import ComponentType
from common.schemas.fields import EnumStr
from observability_api.schemas import ComponentSchema


class PipelineSchema(ComponentSchema):
    type = EnumStr(
        enum=ComponentType,
        load_default=ComponentType.BATCH_PIPELINE.value,
        dump_default=ComponentType.BATCH_PIPELINE.value,
    )
