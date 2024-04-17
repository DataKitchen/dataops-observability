import signal

import pytest
from confluent_kafka import TopicPartition

from common.kafka import KafkaConsumer, KafkaTransactionalConsumer
from common.kafka.consumer import DisconnectedConsumer, GracefulKiller
from common.kafka.errors import ConsumerCommitError, DeserializationError, DisconnectedConsumerError
from common.kafka.topic import JsonV1Topic, MsgPackTopic

CONFIG = {"bootstrap.servers": "127.0.0.1:1337"}


@pytest.mark.unit
@pytest.mark.parametrize("topic", (JsonV1Topic(name="test-topic-json"), MsgPackTopic(name="test-topic-msgpack")))
def test_consumer_init(topic):
    consumer = KafkaConsumer(CONFIG, [topic])
    assert consumer.config == CONFIG
    assert consumer.topics == {topic.name: topic}
    assert consumer.killer == GracefulKiller
    assert type(consumer.consumer) is DisconnectedConsumer
    assert not consumer.consumer


@pytest.mark.unit
@pytest.mark.parametrize("topic", (JsonV1Topic(name="test-topic-json"), MsgPackTopic(name="test-topic-msgpack")))
def test_transactional_consumer_init(topic):
    consumer = KafkaTransactionalConsumer(CONFIG, [topic])
    expected_config = {"isolation.level": "read_committed", "enable.auto.commit": False, **CONFIG}
    assert consumer.config == expected_config
    assert consumer.topics == {topic.name: topic}
    assert consumer.killer == GracefulKiller
    assert type(consumer.consumer) is DisconnectedConsumer
    assert not consumer.consumer


@pytest.mark.unit
def test_consumer_connect_disconnect(json_topic, mocked_confluent_kafka_consumer):
    consumer = KafkaConsumer(CONFIG, [json_topic])
    assert not consumer.consumer
    assert type(consumer.consumer) is DisconnectedConsumer
    consumer.connect()
    assert consumer.consumer == mocked_confluent_kafka_consumer.return_value
    mocked_consumer_instance = consumer.consumer
    mocked_consumer_instance.subscribe.assert_called_once()
    consumer.disconnect()
    assert not consumer.consumer
    assert type(consumer.consumer) is DisconnectedConsumer
    mocked_consumer_instance.close.assert_called_once()


@pytest.mark.unit
def test_consumer_disconnect_unconnected(json_topic):
    consumer = KafkaConsumer(CONFIG, [json_topic])
    assert not consumer.consumer
    consumer.disconnect()
    assert not consumer.consumer
    consumer.disconnect()
    assert not consumer.consumer


@pytest.mark.unit
def test_consumer_disconnected_raises(json_topic):
    consumer = KafkaConsumer(CONFIG, [json_topic])
    assert not consumer.consumer
    with pytest.raises(DisconnectedConsumerError):
        consumer.poll()


@pytest.mark.unit
def test_consumer_get_group_metadata(json_topic, mocked_confluent_kafka_consumer):
    consumer = KafkaConsumer(CONFIG, [json_topic])
    consumer.connect()
    assert consumer.get_group_metadata() == b"unimportantthings"
    mocked_confluent_kafka_consumer.return_value.consumer_group_metadata.assert_called_once()


@pytest.mark.unit
def test_consumer_get_offsets(json_topic, mocked_confluent_kafka_consumer):
    consumer = KafkaConsumer(CONFIG, [json_topic])
    consumer.connect()
    assert consumer.get_offsets() == [TopicPartition(json_topic.name, 0, 0)]
    mocked_confluent_kafka_consumer.return_value.position.assert_called_once()
    mocked_confluent_kafka_consumer.return_value.assignment.assert_called_once()


@pytest.mark.unit
def test_consumer_commit_success(json_topic, mocked_confluent_kafka_consumer):
    offset = 123
    consumer = KafkaConsumer(CONFIG, [json_topic])
    consumer.connect()
    mocked_confluent_kafka_consumer.return_value.commit.return_value = offset
    assert consumer.commit() == offset


@pytest.mark.unit
def test_consumer_commit_error(json_topic, mocked_confluent_kafka_consumer):
    consumer = KafkaConsumer(CONFIG, [json_topic])
    consumer.connect()
    mocked_confluent_kafka_consumer.return_value.commit.side_effect = Exception()
    with pytest.raises(ConsumerCommitError):
        consumer.commit()


@pytest.mark.unit
def test_consumer_poll_json(json_topic, partition, offset, mocked_confluent_kafka_consumer, metric_log_event):
    # consume the message provided by the mock. The mock returns a None first
    consumer = KafkaConsumer(CONFIG, [json_topic])
    consumer.connect()
    msg = consumer.poll()
    assert msg is None
    msg = consumer.poll()
    assert isinstance(msg.payload, metric_log_event.__class__)
    assert msg.payload.pipeline_id == metric_log_event.pipeline_id
    assert msg.topic == json_topic.name
    assert msg.partition == partition
    assert msg.offset == offset


@pytest.mark.unit
def test_consumer_poll_msgpack(
    msgpack_topic, partition, offset, mocked_confluent_kafka_consumer_msgpack, metric_log_event
):
    # consume the message provided by the mock. The mock returns a None first
    consumer = KafkaConsumer(CONFIG, [msgpack_topic])
    consumer.connect()
    msg = consumer.poll()
    assert msg is None
    msg = consumer.poll()
    assert isinstance(msg.payload, metric_log_event.__class__)
    assert msg.payload.pipeline_id == metric_log_event.pipeline_id
    assert msg.topic == msgpack_topic.name
    assert msg.partition == partition
    assert msg.offset == offset


@pytest.mark.unit
def test_consumer_poll_deserialization_error_skipped(json_topic, mocked_confluent_kafka_consumer_bad_data):
    consumer = KafkaConsumer(CONFIG, [json_topic])
    consumer.connect()
    msg = consumer.poll()
    assert msg is None


@pytest.mark.unit
def test_consumer_poll_deserialization_error_raises(json_topic, mocked_confluent_kafka_consumer_bad_data):
    consumer = KafkaConsumer(CONFIG, [json_topic], raise_deserialization_errors=True)
    consumer.connect()
    with pytest.raises(DeserializationError):
        consumer.poll()


@pytest.mark.unit
def test_consumer_iteration(json_topic, mocked_confluent_kafka_consumer, metric_log_event):
    i = 0  # Consume two messages provided by the mock and exit the loop.
    # Since the iteration only yields when a valid message is pool'ed,
    # this loop will run indefinitely if no valid messages are provided.
    for message in KafkaConsumer(CONFIG, [json_topic]):
        i += 1
        if i == 2:
            # ensure the signal is properly killing the internal pooling loop
            signal.raise_signal(signal.SIGINT)
        elif i == 3:
            raise AssertionError("kill signal failed to kill the loop")
        else:
            assert isinstance(message.payload, metric_log_event.__class__)
            assert message.payload.pipeline_key == metric_log_event.pipeline_key
            assert message.topic == json_topic.name
    if i < 2:
        raise AssertionError("pooling loop exited too soon")


@pytest.mark.unit
def test_graceful_killer_sigint():
    killer = GracefulKiller
    killer.init_handlers()
    assert not killer.should_exit
    signal.raise_signal(signal.SIGINT)
    assert killer.should_exit


@pytest.mark.unit
def test_graceful_killer_sigterm():
    killer = GracefulKiller
    killer.init_handlers()
    assert not killer.should_exit
    signal.raise_signal(signal.SIGTERM)
    assert killer.should_exit
