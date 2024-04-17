__all__ = ["KafkaMessage"]
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, kw_only=True)
class KafkaMessage(Generic[T]):
    """
    A generic Kafka message

    It is mainly used to convey payload and metadata info to consumers. The
    payload type is determined by the topic.
    """

    payload: T
    topic: str
    partition: int
    offset: int
    headers: dict
    key: Optional[str] = None
