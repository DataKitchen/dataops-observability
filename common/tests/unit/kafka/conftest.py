from itertools import cycle
from unittest.mock import MagicMock, patch

import pytest
from confluent_kafka import KafkaError, KafkaException, TopicPartition

from common.kafka.topic import JsonV1Topic, MsgPackTopic
from common.messagepack import dumps as msgpack_dumps
from testlib.fixtures.v1_events import *


@pytest.fixture
def topic_name():
    yield "test_topic"


@pytest.fixture
def json_topic(topic_name):
    yield JsonV1Topic(name=topic_name)


@pytest.fixture
def msgpack_topic(topic_name):
    yield MsgPackTopic(name=topic_name)


@pytest.fixture
def partition():
    yield 8


@pytest.fixture
def offset():
    yield 7


@pytest.fixture
def metric_log_event_bytes(metric_log_event):
    yield metric_log_event.as_bytes()


@pytest.fixture
def mocked_kafka_message(metric_log_event_bytes, topic_name, partition, offset):
    # confluent_kafka.Message instances cannot be created, using a mock instead
    message = MagicMock()
    message.error = MagicMock(return_value=None)
    message.value = MagicMock(return_value=metric_log_event_bytes)
    message.headers = MagicMock(return_value=[])
    message.topic = MagicMock(return_value=topic_name)
    message.offset = MagicMock(return_value=offset)
    message.partition = MagicMock(return_value=partition)
    yield message


@pytest.fixture
def mocked_kafka_message_msgpack(metric_log_event, topic_name, partition, offset):
    # confluent_kafka.Message instances cannot be created, using a mock instead
    message = MagicMock()
    message.error = MagicMock(return_value=None)
    message.value = MagicMock(return_value=msgpack_dumps(metric_log_event))
    message.headers = MagicMock(return_value=[(b"Content-Type", b"application/msgpack")])
    message.topic = MagicMock(return_value=topic_name)
    message.offset = MagicMock(return_value=offset)
    message.partition = MagicMock(return_value=partition)
    yield message


@pytest.fixture
def kafka_error():
    error = KafkaError(1)
    yield error


@pytest.fixture
def kafka_exception(kafka_error):
    e = KafkaException()
    e.args = (kafka_error,)
    yield e


@pytest.fixture
def mocked_kafka_message_bad_data(mocked_kafka_message):
    mocked_kafka_message.value.return_value = b"\x00"
    yield mocked_kafka_message


@pytest.fixture
def mocked_confluent_kafka_consumer(mocked_kafka_message, topic_name):
    with patch("common.kafka.consumer.Consumer") as ck_consumer:
        instance = ck_consumer.return_value
        # consumer will see one message every 2 poll calls
        instance.poll.side_effect = cycle([None, mocked_kafka_message])
        # consumer_group_metadata returns an internal object used for a producer function
        instance.consumer_group_metadata.return_value = b"unimportantthings"
        instance.position.return_value = [TopicPartition(topic_name, 0, 0)]
        instance.assignment.return_value = [TopicPartition(topic_name, 0)]
        yield ck_consumer


@pytest.fixture
def mocked_confluent_kafka_consumer_msgpack(mocked_kafka_message_msgpack, topic_name):
    with patch("common.kafka.consumer.Consumer") as ck_consumer:
        instance = ck_consumer.return_value
        # consumer will see one message every 2 poll calls
        instance.poll.side_effect = cycle([None, mocked_kafka_message_msgpack])
        # consumer_group_metadata returns an internal object used for a producer function
        instance.consumer_group_metadata.return_value = b"unimportantthings"
        instance.position.return_value = [TopicPartition(topic_name, 0, 0)]
        instance.assignment.return_value = [TopicPartition(topic_name, 0)]
        yield ck_consumer


@pytest.fixture
def mocked_confluent_kafka_consumer_bad_data(mocked_confluent_kafka_consumer, mocked_kafka_message_bad_data):
    mocked_confluent_kafka_consumer.return_value.poll.side_effect = cycle([mocked_kafka_message_bad_data])
    yield mocked_confluent_kafka_consumer


@pytest.fixture
def mocked_confluent_kafka_producer():
    with patch("common.kafka.producer.Producer") as ck_producer:
        instance = ck_producer.return_value
        instance.produce.return_value = None
        instance.poll.return_value = None
        instance.flush.return_value = None
        instance.abort_transaction.return_value = None
        instance.begin_transaction.return_value = None
        instance.send_offsets_to_transaction.return_value = None
        instance.commit_transaction.return_value = None
        instance.init_transactions.return_value = None
        yield ck_producer


@pytest.fixture(autouse=True)
def mocked_sleep():
    with patch("time.sleep") as sleep:
        yield sleep
