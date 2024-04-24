__all__ = ["StreamingPipelineSchema"]

from common.entities.component import ComponentType
from common.schemas.fields import EnumStr
from observability_api.schemas import ComponentSchema


class StreamingPipelineSchema(ComponentSchema):
    type = EnumStr(
        enum=ComponentType,
        load_default=ComponentType.STREAMING_PIPELINE.value,
        dump_default=ComponentType.STREAMING_PIPELINE.value,
    )
