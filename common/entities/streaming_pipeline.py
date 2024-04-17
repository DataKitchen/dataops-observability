__all__ = ["StreamingPipeline"]


from .base_entity import BaseModel
from .component import ComponentType
from .component_meta import SimpleComponentMeta


class StreamingPipeline(BaseModel, metaclass=SimpleComponentMeta):
    """Representation of a streaming-pipeline component in the application."""

    component_type = ComponentType.STREAMING_PIPELINE.name
