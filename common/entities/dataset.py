__all__ = ["Dataset"]


from .base_entity import BaseModel
from .component import ComponentType
from .component_meta import SimpleComponentMeta


class Dataset(BaseModel, metaclass=SimpleComponentMeta):
    """Representation of a dataset component in the application."""

    component_type = ComponentType.DATASET.name
