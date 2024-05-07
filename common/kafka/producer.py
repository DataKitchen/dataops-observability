from __future__ import annotations

__all__ = ["DisconnectedProducer", "KafkaProducer", "KafkaTransactionalProducer"]

import logging
import uuid
from contextlib import contextmanager
from types import TracebackType
from typing import Any, Callable, Generator, Optional, Type

from confluent_kafka import KafkaError, KafkaException, Message, Producer

from common.kafka.consumer import KafkaTransactionalConsumer
from common.kafka.errors import (
    DisconnectedProducerError,
    MessageTooLargeError,
    ProducerConfigurationError,
    ProducerError,
    ProducerTransactionError,
    SerializationError,
)
from common.kafka.settings import (
    KAFKA_OP_TIMEOUT_SECS,
    PRODUCER_MANDATORY_SETTINGS,
    PRODUCER_TX_COMMIT_TIMEOUT_SECS,
    PRODUCER_TX_MANDATORY_SETTINGS,
    PRODUCER_TX_OPS_TIMEOUT_SECS,
)
from common.kafka.topic import Topic
from conf import settings

LOG = logging.getLogger(__name__)


class DisconnectedProducer(Producer):
    """
    Internal class to help with typing, instead of KafkaProducer.producer being an `Optional[Producer]` it can be a Producer.
    All accesses before connecting will raise a DisconnectedProducerError. This is a lot DRYer than performing an assert before each access.
    Additionally, an instance evaluates to false when coerced to boolean, allowing easy use on if statements.
    """

    def __init__(self) -> None:
        pass

    def __getattribute__(self, __name: str) -> Any:
        raise DisconnectedProducerError("Producer needs to be connected first")

    def __bool__(self) -> bool:
        return False


class KafkaProducer:
    """
    Interface to produce messages to Kafka. Provides a context manager to handle connecting to kafka.
    If not using the context manager, connect and disconnect should be called before and after producing messages.

    The producer library has built in support for retrying failed messages. Note that the order of the messages
    are not guaranteed when retrying unless configuration option "enable.idempotence" is set to true.

    Connection configuration is loaded from the environment. User can pass other settings to the constructor.
    System-wide required settings cannot be overridden.

    Usage example:
        with KafkaProducer({}) as producer:
            producer.produce("MY_TOPIC_NAME", event)

    Config reference docs: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md

    """

    def __init__(self, config: dict) -> None:
        if PRODUCER_MANDATORY_SETTINGS.keys() & config.keys():
            raise ProducerConfigurationError(
                f"Local configuration cannot override any of {PRODUCER_MANDATORY_SETTINGS.keys()}"
            )
        self.producer = DisconnectedProducer()
        self.config = {
            **config,
            # Environment settings can override settings from the call site
            **settings.KAFKA_CONNECTION_PARAMS,
            # Mandatory settings overrides any previous settings
            **PRODUCER_MANDATORY_SETTINGS,
        }

    def __enter__(self) -> KafkaProducer:
        self.connect()
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        self.disconnect()

    def connect(self) -> None:
        if not self.producer:
            self.producer = Producer(self.config)

    def disconnect(self) -> None:
        if self.producer:
            self.producer.flush()
            self.producer = DisconnectedProducer()

    def is_topic_available(self, topic: Topic, timeout: int = KAFKA_OP_TIMEOUT_SECS) -> bool:
        metadata = self.producer.list_topics(topic=topic.name, timeout=timeout)
        return len(metadata.topics[topic.name].partitions) > 0

    def produce(self, topic: Topic, event: Any, callback: Optional[Callable] = None) -> None:
        def delivery_report(err: KafkaError, message: Message) -> None:
            """Called once for each message produced to indicate delivery result. Triggered by poll() or flush()."""
            if err is not None:
                raise ProducerError(f"Failed to produce message: {err}")
            LOG.debug("Message delivered to %s [%s]", message.topic(), message.partition())

        callback = callback or delivery_report
        try:
            message = topic.serialize(event)
        except Exception as ex:
            raise SerializationError("Error serializing message") from ex
        try:
            produce_kwargs = message.as_dict()
            produce_kwargs["callback"] = callback
            self.producer.produce(**produce_kwargs)
            self.producer.poll(0)
        except DisconnectedProducerError:
            raise
        except KafkaException as ex:
            if ex.args[0].code() == KafkaError.MSG_SIZE_TOO_LARGE:
                raise MessageTooLargeError("Payload is too large to fit into a single Kafka message")
            else:
                raise ProducerError("Error producing message to Kafka") from ex
        except Exception as ex:
            raise ProducerError("Unexpected error producing message to Kafka") from ex


class KafkaTransactionalProducer(KafkaProducer):
    """
    Can be used to guarantee all produced messages from the same context block are sent or discarded atomically.
    If not using a context manager, connect(), begin_tx() and commit_tx() need to be invoked.
    Can be used together with a TransactionalConsumer to guarantee message consumption + production is atomic.

    usage example:
        with KafkaTransactionalProducer({}}) as producer:
            with producer.transaction():
                producer.produce("MY_FAVORITE_TOPIC", event, delivery_callback)
                producer.produce("SOME_OTHER_TOPIC", event_2)

    configuration: see KafkaProducer

    """

    def __init__(self, config: dict, tx_consumer: Optional[KafkaTransactionalConsumer] = None) -> None:
        if PRODUCER_TX_MANDATORY_SETTINGS.keys() & config.keys():
            raise ProducerConfigurationError(
                f"Local configuration cannot override any of {PRODUCER_TX_MANDATORY_SETTINGS.keys()}"
            )
        config = {
            **config,
            **PRODUCER_TX_MANDATORY_SETTINGS,
        }
        if "transactional.id" not in config:
            config["transactional.id"] = str(uuid.uuid4())
        self.tx_consumer = tx_consumer
        super().__init__(config)

    def connect(self) -> None:
        if not self.producer:
            super().connect()
            self.producer.init_transactions(PRODUCER_TX_OPS_TIMEOUT_SECS)

    def begin_tx(self) -> None:
        self.producer.begin_transaction()

    def abort_tx(self) -> None:
        self.producer.abort_transaction(PRODUCER_TX_OPS_TIMEOUT_SECS)

    def commit_tx(self) -> None:
        if self.tx_consumer:
            self.producer.send_offsets_to_transaction(
                self.tx_consumer.get_offsets(),
                self.tx_consumer.get_group_metadata(),
                # Docs say this argument is in seconds, but it's actually milliseconds
                PRODUCER_TX_OPS_TIMEOUT_SECS * 1000,
            )
        self.producer.commit_transaction(PRODUCER_TX_COMMIT_TIMEOUT_SECS)

    @contextmanager
    def transaction(self) -> Generator[KafkaTransactionalProducer, None, None]:
        try:
            self.begin_tx()
            yield self
            self.producer.flush()
            self.commit_tx()
        except KafkaException as e:
            # Certain errors requires aborting the transaction. Retriable
            # errors are also aborted since the retry logic is performed by
            # restarting the process. Any other errors are fatal and cannot be
            # handled.
            # https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#confluent_kafka.Producer.commit_transaction
            LOG.exception("Exception in KafkaTransactionalProducer transaction")
            if e.args[0].retriable() or e.args[0].txn_requires_abort():
                LOG.error("Aborting transaction")
                self.abort_tx()
            raise ProducerTransactionError from e
        except Exception:
            LOG.exception("Exception in KafkaTransactionalProducer, aborting transaction")
            self.abort_tx()
            raise
