__all__ = ["KafkaConsumer", "KafkaTransactionalConsumer"]

import logging
import signal
from types import FrameType
from typing import Any, Iterator, Optional, Type

from confluent_kafka import Consumer, Message

from common.kafka.errors import (
    ConsumerCommitError,
    ConsumerConfigurationError,
    ConsumerError,
    DeserializationError,
    DisconnectedConsumerError,
    MessageError,
)
from common.kafka.message import KafkaMessage
from common.kafka.settings import CONSUMER_POLL_PERIOD_SECS, CONSUMER_TX_MANDATORY_SETTINGS
from common.kafka.topic import Topic
from conf import settings

LOG = logging.getLogger(__name__)


def log_consumer_assignments(consumer: Consumer, partitions: list) -> None:
    partitions_formatted = "; ".join(sorted([f"{p.topic}:{p.partition}:{p.offset}" for p in partitions]))
    LOG.info(f"Consumer assigned to partitions: {partitions_formatted};")


def log_consumer_revoke(consumer: Consumer, partitions: list) -> None:
    LOG.info("Consumer topic assignments were revoked")


class GracefulKiller:
    """
    Default loop controller for the `KafkaConsumer` and subclasses.
    Intercepts `SIGINT` and `SIGTERM` to let the consumer know it should stop pooling for messages and exit.
    The python process will still exit upon receiving `SIGKILL`, which should be sent after the graceful period is over.
    """

    should_exit = False

    @staticmethod
    def init_handlers() -> None:
        GracefulKiller.should_exit = False
        signal.signal(signal.SIGINT, GracefulKiller.exit_gracefully)
        signal.signal(signal.SIGTERM, GracefulKiller.exit_gracefully)

    @staticmethod
    def exit_gracefully(sig_num: int, frame: Optional[FrameType]) -> Any:
        LOG.info(f"Signal {sig_num} received, attempting to exit gracefully. Use SIGKILL to terminate immediately.")
        GracefulKiller.should_exit = True


class DisconnectedConsumer(Consumer):
    """
    Internal class to help with typing, instead of `KafkaConsumer.consumer` being an `Optional[Consumer]`, it can just
    be a `Consumer`. All accesses before connecting will raise a `DisconnectedConsumerError`. This is a lot DRYer than
    performing an assert before each access. Additionally, an instance evaluates to false when coerced to boolean,
    allowing easy use on if statements.
    """

    def __init__(self) -> None:
        pass

    def __getattribute__(self, __name: str) -> Any:
        raise DisconnectedConsumerError("Consumer needs to be connected first")

    def __bool__(self) -> bool:
        return False


class KafkaConsumer:
    """
    Consumer using consumer groups to continuously consume messages from te subscribed topics.
    Multiple workers of the same group can be spawned, allowing parallel consumption of different partitions.

    Connection configuration is loaded from the environment. User can pass other settings to the constructor.
    System-wide required settings cannot be overridden.

    Usage example:
        consumer_config = {
            "reconnect.backoff.ms": 200,
            "group.id": "xyz-consumer",
        }

        for message in KafkaConsumer(consumer_config, ["TOPIC_COOL_EVENTS"]):
            handle_event(event)

    Config reference docs: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    """

    def __init__(
        self,
        config: dict[str, Any],
        topics: list[Topic],
        killer: Type[GracefulKiller] = GracefulKiller,
        raise_deserialization_errors: bool = False,
    ) -> None:
        self.consumer: Consumer = DisconnectedConsumer()
        self.config = {
            **config,
            # Environment settings can override settings from the call site
            **settings.KAFKA_CONNECTION_PARAMS,
        }
        if not topics:
            raise ConsumerConfigurationError("A non empty list of topics needs to be provided")
        self.topics = {topic.name: topic for topic in topics}
        self.killer = killer
        self.killer.init_handlers()
        self.raise_deserialization_errors = raise_deserialization_errors

    def __iter__(self) -> Iterator[KafkaMessage]:
        self.connect()
        while not self.killer.should_exit:
            try:
                message = self.poll()

                if not message:
                    LOG.debug("Waiting for message...")
                    continue
                yield message
            except (ConsumerError, MessageError):
                LOG.critical("Error receiving message", exc_info=True)
                raise
        self.disconnect()

    def connect(self) -> None:
        if not self.consumer:
            self.consumer = Consumer(self.config)
            self.consumer.subscribe(
                list(self.topics.keys()), on_assign=log_consumer_assignments, on_revoke=log_consumer_revoke
            )

    def disconnect(self) -> None:
        if self.consumer:
            self.consumer.close()
            self.consumer = DisconnectedConsumer()

    def get_group_metadata(self) -> Any:
        return self.consumer.consumer_group_metadata()

    def get_offsets(self) -> Any:
        return self.consumer.position(self.consumer.assignment())

    def commit(self) -> Any:
        """Commit until last consumed message"""
        try:
            return self.consumer.commit(asynchronous=False)
        except Exception as e:
            raise ConsumerCommitError from e

    def poll(self) -> Optional[KafkaMessage]:
        try:
            msg: Optional[Message] = self.consumer.poll(CONSUMER_POLL_PERIOD_SECS)
        except DisconnectedConsumerError:
            raise
        except Exception as ex:
            raise ConsumerError("Error pooling for messages") from ex
        if msg is None:
            return None
        elif msg.error():
            raise MessageError(msg.error())
        try:
            topic = self.topics[msg.topic()]
        except KeyError:
            raise MessageError(
                "Unable to find the correct topic for message deserialization",
                msg.topic(),
                self.topics.keys(),
            )
        try:
            message = topic.deserialize(msg)
        except Exception as ex:
            if self.raise_deserialization_errors:
                raise DeserializationError(
                    "Error deserializing consumed message", msg.topic(), msg.partition(), msg.offset()
                ) from ex
            LOG.exception(f"Error deserializing consumed message {msg.topic()}:{msg.partition()}:{msg.offset()}")
            msg_payload = msg.value().hex("-", 8) if topic.binary else msg.value().decode("utf-8")
            LOG.debug("Caused by message payload %s", msg_payload)
            return None
        return message


class KafkaTransactionalConsumer(KafkaConsumer):
    """
    This consumer is meant to be used together with KafkaTransactionalProducer, since consumers themselves do not
    support transactions. If an error occurs during handling of the message then the consumer's last message offset
    remains uncommitted. The process should exit to allow a new worker to be spawned and consume the same message again.

    Usage example:
        consumer = KafkaTransactionalConsumer(consumer_config, ["THE_TOPIC"])
        with KafkaTransactionalProducer(producer_config, tx_consumer=consumer) as producer:
            for in_event in consumer:
                with producer.transaction():
                    out_event = handle_event(in_event)
                    producer.produce("SOME_OTHER_TOPIC", out_event)

    configuration: see KafkaConsumer
    """

    def __init__(
        self, config: dict[str, Any], topics: list[Topic], killer: Type[GracefulKiller] = GracefulKiller
    ) -> None:
        if CONSUMER_TX_MANDATORY_SETTINGS.keys() & config.keys():
            raise ConsumerConfigurationError(
                f"Local configuration cannot override any of {CONSUMER_TX_MANDATORY_SETTINGS.keys()}"
            )
        config = {**config, **CONSUMER_TX_MANDATORY_SETTINGS}
        super().__init__(config, topics, killer)
