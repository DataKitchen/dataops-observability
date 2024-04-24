__all__ = ["EventInterface"]

import json
from typing import Any, Type, TypeVar

from common.events.v1.event_schemas import EventApiSchema, EventSchema, EventSchemaInterface

EventInterfaceType = TypeVar("EventInterfaceType", bound="EventInterface")


class EventInterface:
    """
    This class is the interface to the Event system.

    It is separate so that the methods may be over-loaded without having to deal with Event's data-members.
    Most classes should inherit from Event.
    """

    __schema__: Type[EventSchemaInterface] = EventSchema
    __api_schema__: Type[EventApiSchema] = EventApiSchema
    """
    A reference to a Marshmallow schema defined for the subclassed Events. It will be used for all deserialization,
    and for validation of the fields during that deserialization. Must be subclassed.
    """

    @property
    def partition_identifier(self) -> str:
        """Used by the Messaging system to identify key of the event. It's here as an Abstract method for mypy."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls: Type[EventInterfaceType], data: dict, **kwargs: Any) -> EventInterfaceType:
        if cls.__schema__ is EventSchema:
            raise AttributeError("Subclasses of Event must define its own '__schema__'")
        return cls(**cls.__schema__(**kwargs).load(data))

    @classmethod
    def from_bytes(cls: Type[EventInterfaceType], data: bytes) -> EventInterfaceType:
        return cls.from_dict(json.loads(data.decode("utf-8")))

    def as_dict(self) -> dict:
        if self.__schema__ is EventSchema:
            raise AttributeError("Subclasses of Event must define its own '__schema__'")
        ret: dict = self.__schema__().dump(self)
        return ret

    def as_bytes(self) -> bytes:
        return json.dumps(self.as_dict()).encode("utf-8")
