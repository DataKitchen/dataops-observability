__all__ = [
    "PayloadInterface",
    "TOPIC_IDENTIFIED_EVENTS",
    "TOPIC_UNIDENTIFIED_EVENTS",
    "TOPIC_SCHEDULED_EVENTS",
    "TOPIC_DEAD_LETTER_OFFICE",
]


import json
from dataclasses import dataclass
from typing import Any, NamedTuple, Protocol

from confluent_kafka import Message

from common import messagepack as msgpack
from common.events.v1 import EventInterface, instantiate_event_from_data
from common.kafka.message import KafkaMessage


class PayloadInterface(Protocol):
    @property
    def partition_identifier(self) -> str:
        raise NotImplementedError


class ProduceMessageArgs(NamedTuple):
    # data container to pass necessary values from topic serialization to producer's produce call
    value: bytes
    topic: str
    headers: dict[str, str]
    key: str | None = None

    def as_dict(self) -> dict[str, Any]:
        d = {
            "topic": self.topic,
            "value": self.value,
            "headers": self.headers,
        }
        if self.key is not None:
            # if the key is None, then we shouldn't pass it to kafka's produce() call,
            # otherwise all messages go to a single partition instead of being randomly distributed
            d["key"] = self.key
        return d


def _get_headers_as_dict(headers: list[tuple[str, bytes]] | None) -> dict[str, str]:
    return {k: v.decode("utf-8") for k, v in headers or {}}


@dataclass(frozen=True, kw_only=True)
class Topic:
    name: str
    binary: bool = False

    def serialize(self, event: Any) -> ProduceMessageArgs:
        raise NotImplementedError

    def deserialize(self, message: Message) -> KafkaMessage:
        raise NotImplementedError


@dataclass(frozen=True, kw_only=True)
class JsonV1Topic(Topic):
    def serialize(self, event: EventInterface) -> ProduceMessageArgs:
        return ProduceMessageArgs(value=event.as_bytes(), topic=self.name, headers={}, key=event.partition_identifier)

    def deserialize(self, message: Message) -> KafkaMessage[EventInterface]:
        msg_data = json.loads(message.value().decode("utf-8"))
        return KafkaMessage[EventInterface](
            payload=instantiate_event_from_data(msg_data),
            topic=message.topic(),
            partition=message.partition(),
            offset=message.offset(),
            headers=_get_headers_as_dict(message.headers()),
            key=message.key(),
        )


@dataclass(frozen=True, kw_only=True)
class MsgPackTopic(Topic):
    binary: bool = True

    def serialize(self, event: PayloadInterface) -> ProduceMessageArgs:
        return ProduceMessageArgs(
            value=msgpack.dumps(event),
            topic=self.name,
            headers={"Content-Type": "application/msgpack"},
            key=event.partition_identifier,
        )

    def deserialize(self, message: Message) -> KafkaMessage:
        return KafkaMessage[PayloadInterface](
            payload=msgpack.loads(message.value()),
            topic=message.topic(),
            partition=message.partition(),
            offset=message.offset(),
            headers=_get_headers_as_dict(message.headers()),
            key=message.key(),
        )


@dataclass(frozen=True, kw_only=True)
class MixedTopic(Topic):
    """
    This class mix JSON and msgpack serialization in the same topic.

    It is created as an interim solution as JSON serialization is graudally phased out. It should not be used more than
    what is necessary.
    """

    binary: bool = True  # and False

    def serialize(self, event: EventInterface | PayloadInterface) -> ProduceMessageArgs:
        if isinstance(event, EventInterface):
            return ProduceMessageArgs(
                value=event.as_bytes(), topic=self.name, headers={}, key=event.partition_identifier
            )
        else:
            return ProduceMessageArgs(
                value=msgpack.dumps(event),
                topic=self.name,
                headers={"Content-Type": "application/msgpack"},
                key=event.partition_identifier,
            )

    def deserialize(self, message: Message) -> KafkaMessage[EventInterface] | KafkaMessage[PayloadInterface]:
        if not message.headers():
            msg_data = json.loads(message.value().decode("utf-8"))
            return KafkaMessage[EventInterface](
                payload=instantiate_event_from_data(msg_data),
                topic=message.topic(),
                partition=message.partition(),
                offset=message.offset(),
                headers=_get_headers_as_dict(message.headers()),
                key=message.key(),
            )
        else:
            return KafkaMessage[PayloadInterface](
                payload=msgpack.loads(message.value()),
                topic=message.topic(),
                partition=message.partition(),
                offset=message.offset(),
                headers=_get_headers_as_dict(message.headers()),
                key=message.key(),
            )


TOPIC_IDENTIFIED_EVENTS = MixedTopic(name="IdentifiedEvents")
"""Kafka topic for identified events."""

TOPIC_UNIDENTIFIED_EVENTS = JsonV1Topic(name="UnidentifiedEvents")
"""Kafka topic for unidentified events."""

TOPIC_SCHEDULED_EVENTS = MsgPackTopic(name="ScheduledEvents")
"""Kafka topic for scheduled events."""

TOPIC_DEAD_LETTER_OFFICE = JsonV1Topic(name="DeadLetterOffice")
"""Kafka topic for any event that isn't recognizable by the system """
