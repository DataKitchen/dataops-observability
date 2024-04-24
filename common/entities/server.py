__all__ = ["Server"]


from .base_entity import BaseModel
from .component import ComponentType
from .component_meta import SimpleComponentMeta


class Server(BaseModel, metaclass=SimpleComponentMeta):
    """Representation of a server component in the application."""

    component_type = ComponentType.SERVER.name
