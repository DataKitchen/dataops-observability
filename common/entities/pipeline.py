__all__ = ["Pipeline"]


from .base_entity import BaseModel
from .component import ComponentType
from .component_meta import SimpleComponentMeta


class Pipeline(BaseModel, metaclass=SimpleComponentMeta):
    """Representation of a batch-pipeline component in the application."""

    component_type = ComponentType.BATCH_PIPELINE.name
