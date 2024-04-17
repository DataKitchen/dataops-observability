from unittest.mock import patch

import pytest
from confluent_kafka import KafkaError, KafkaException

from common.kafka import (
    KafkaProducer,
    KafkaTransactionalConsumer,
    KafkaTransactionalProducer,
    ProducerError,
    ProducerTransactionError,
)
from common.kafka.errors import DisconnectedProducerError, MessageTooLargeError
from common.kafka.producer import DisconnectedProducer
from common.kafka.settings import KAFKA_TX_TIMEOUT_MILISECS

CONFIG = {"bootstrap.servers": "127.0.0.1:1337"}


@pytest.mark.unit
def test_producer_init(mocked_confluent_kafka_producer):
    expected_config = {
        "request.required.acks": "all",
        **CONFIG,
    }
    producer = KafkaProducer(CONFIG)
    assert producer.config == expected_config
    assert type(producer.producer) is DisconnectedProducer
    assert not producer.producer


@pytest.mark.unit
def test_transactional_producer_init(mocked_confluent_kafka_producer):
    with patch("common.kafka.producer.uuid.uuid4") as uuuid4_mock:
        uuid = "aaaa-1111-aaaa"
        uuuid4_mock.return_value = uuid
        expected_config = {
            "enable.idempotence": True,
            "transactional.id": uuid,
            "transaction.timeout.ms": KAFKA_TX_TIMEOUT_MILISECS,
            "request.required.acks": "all",
            **CONFIG,
        }
        producer = KafkaTransactionalProducer(CONFIG)
        assert producer.config == expected_config
        assert type(producer.producer) is DisconnectedProducer
        assert not producer.producer


@pytest.mark.unit
def test_producer_connect_disconnect(mocked_confluent_kafka_producer):
    producer = KafkaProducer(CONFIG)
    assert not producer.producer
    producer.connect()
    assert producer.producer == mocked_confluent_kafka_producer.return_value
    producer.disconnect()
    assert not producer.producer


@pytest.mark.unit
def test_transactional_producer_connect_disconnect_idempotent(mocked_confluent_kafka_producer):
    producer = KafkaTransactionalProducer(CONFIG)
    assert not producer.producer
    producer.connect()
    assert producer.producer == mocked_confluent_kafka_producer.return_value
    mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()

    # call connect again and make sure init_transaction was only called the first time
    producer.connect()
    assert producer.producer == mocked_confluent_kafka_producer.return_value
    mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()

    with producer:
        pass
    mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()
    mocked_confluent_kafka_producer.return_value.flush.assert_called_once()
    producer.disconnect()
    mocked_confluent_kafka_producer.return_value.flush.assert_called_once()
    assert not producer.producer


@pytest.mark.unit
def test_producer_disconnect_unconnected(mocked_confluent_kafka_producer):
    producer = KafkaProducer(CONFIG)
    assert not producer.producer
    producer.disconnect()
    assert not producer.producer
    producer.disconnect()
    assert not producer.producer


@pytest.mark.unit
def test_producer_unconnected_raises(mocked_confluent_kafka_producer, json_topic, metric_log_event):
    producer = KafkaProducer(CONFIG)
    assert not producer.producer
    with pytest.raises(DisconnectedProducerError):
        producer.produce(json_topic, metric_log_event)


@pytest.mark.unit
def test_producer_context_manager(mocked_confluent_kafka_producer):
    with KafkaProducer(CONFIG) as producer:
        assert producer.producer == mocked_confluent_kafka_producer.return_value
    mocked_confluent_kafka_producer.return_value.flush.assert_called_once()
    assert not producer.producer


@pytest.mark.unit
def test_transactional_producer_context_manager(mocked_confluent_kafka_producer):
    with KafkaTransactionalProducer(CONFIG) as producer:
        assert producer.producer == mocked_confluent_kafka_producer.return_value
        mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()
        mocked_confluent_kafka_producer.return_value.begin_transaction.assert_not_called()
        mocked_confluent_kafka_producer.return_value.commit_transaction.assert_not_called()
    assert not producer.producer
    mocked_confluent_kafka_producer.return_value.flush.assert_called_once()
    mocked_confluent_kafka_producer.return_value.commit_transaction.assert_not_called()
    mocked_confluent_kafka_producer.return_value.abort_transaction.assert_not_called()


@pytest.mark.unit
def test_transactional_producer_transaction(mocked_confluent_kafka_producer):
    with KafkaTransactionalProducer(CONFIG) as producer:
        assert producer.producer == mocked_confluent_kafka_producer.return_value
        mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()
        with producer.transaction():
            mocked_confluent_kafka_producer.return_value.begin_transaction.assert_called_once()
            mocked_confluent_kafka_producer.return_value.commit_transaction.assert_not_called()
        mocked_confluent_kafka_producer.return_value.flush.assert_called_once()
        mocked_confluent_kafka_producer.return_value.commit_transaction.assert_called_once()
        mocked_confluent_kafka_producer.return_value.send_offsets_to_transaction.assert_not_called()
        mocked_confluent_kafka_producer.return_value.abort_transaction.assert_not_called()
    assert not producer.producer
    assert mocked_confluent_kafka_producer.return_value.flush.call_count == 2


@pytest.mark.unit
def test_transactional_producer_context_manager_aborts_exception(mocked_confluent_kafka_producer):
    class FakeException(Exception):
        pass

    with pytest.raises(FakeException):
        with KafkaTransactionalProducer(CONFIG) as producer:
            assert producer.producer is not None
            mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()
            with producer.transaction():
                mocked_confluent_kafka_producer.return_value.begin_transaction.assert_called_once()
                mocked_confluent_kafka_producer.return_value.commit_transaction.assert_not_called()
                raise FakeException
    mocked_confluent_kafka_producer.return_value.commit_transaction.assert_not_called()
    mocked_confluent_kafka_producer.return_value.abort_transaction.assert_called_once()
    mocked_confluent_kafka_producer.return_value.send_offsets_to_transaction.assert_not_called()


@pytest.mark.unit
def test_transactional_producer_commit_consumer_offset(
    mocked_confluent_kafka_producer, mocked_confluent_kafka_consumer, json_topic
):
    consumer = KafkaTransactionalConsumer(CONFIG, [json_topic])
    consumer.connect()
    with KafkaTransactionalProducer(CONFIG, tx_consumer=consumer) as producer:
        assert producer.tx_consumer == consumer
        assert producer.producer is not None
        mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()
        with producer.transaction():
            mocked_confluent_kafka_producer.return_value.begin_transaction.assert_called_once()
            mocked_confluent_kafka_producer.return_value.commit_transaction.assert_not_called()
            mocked_confluent_kafka_producer.return_value.abort_transaction.assert_not_called()
            mocked_confluent_kafka_producer.return_value.send_offsets_to_transaction.assert_not_called()
        mocked_confluent_kafka_producer.return_value.commit_transaction.assert_called_once()
        mocked_confluent_kafka_producer.return_value.send_offsets_to_transaction.assert_called_once()
        mocked_confluent_kafka_consumer.return_value.position.assert_called_once()
        mocked_confluent_kafka_consumer.return_value.assignment.assert_called_once()


@pytest.mark.unit
def test_producer_produce_event_json(
    mocked_confluent_kafka_producer, json_topic, metric_log_event, mocked_kafka_message
):
    with KafkaProducer(CONFIG) as producer:
        producer.produce(json_topic, metric_log_event)
        mocked_confluent_kafka_producer.return_value.produce.assert_called_once()
        assert mocked_confluent_kafka_producer.return_value.produce.call_args[1]["topic"] == json_topic.name
        delivery_report = mocked_confluent_kafka_producer.return_value.produce.call_args[1]["callback"]
        delivery_report(None, mocked_kafka_message)
    mocked_confluent_kafka_producer.return_value.flush.assert_called_once()


@pytest.mark.unit
def test_producer_produce_event_msgpack(
    mocked_confluent_kafka_producer, msgpack_topic, metric_log_event, mocked_kafka_message
):
    with KafkaProducer(CONFIG) as producer:
        producer.produce(msgpack_topic, metric_log_event)
        mocked_confluent_kafka_producer.return_value.produce.assert_called_once()
        assert mocked_confluent_kafka_producer.return_value.produce.call_args[1]["topic"] == msgpack_topic.name
        delivery_report = mocked_confluent_kafka_producer.return_value.produce.call_args[1]["callback"]
        delivery_report(None, mocked_kafka_message)
    mocked_confluent_kafka_producer.return_value.flush.assert_called_once()


@pytest.mark.unit
def test_producer_produce_callback_error(
    mocked_confluent_kafka_producer, json_topic, metric_log_event, kafka_error, mocked_kafka_message, mocked_sleep
):
    with pytest.raises(ProducerError):
        with KafkaProducer(CONFIG) as producer:
            producer.produce(json_topic, metric_log_event)
            delivery_report = mocked_confluent_kafka_producer.return_value.produce.call_args[1]["callback"]
            delivery_report(kafka_error, mocked_kafka_message)
    mocked_confluent_kafka_producer.return_value.produce.assert_called_once()
    mocked_confluent_kafka_producer.return_value.flush.assert_called_once()


@pytest.mark.unit
def test_transactional_producer_produce(
    mocked_confluent_kafka_producer, json_topic, metric_log_event, mocked_kafka_message
):
    with KafkaTransactionalProducer(CONFIG) as producer:
        with producer.transaction():
            producer.produce(json_topic, metric_log_event)
            mocked_confluent_kafka_producer.return_value.produce.assert_called_once()
            delivery_report = mocked_confluent_kafka_producer.return_value.produce.call_args[1]["callback"]
            delivery_report(None, mocked_kafka_message)
        mocked_confluent_kafka_producer.return_value.flush.assert_called_once()
        mocked_confluent_kafka_producer.return_value.init_transactions.assert_called_once()
        mocked_confluent_kafka_producer.return_value.begin_transaction.assert_called_once()
        mocked_confluent_kafka_producer.return_value.commit_transaction.assert_called_once()
        mocked_confluent_kafka_producer.return_value.abort_transaction.assert_not_called()
        mocked_confluent_kafka_producer.return_value.send_offsets_to_transaction.assert_not_called()


@pytest.mark.unit
def test_transactional_producer_raises_transaction_error_begin_tx(mocked_confluent_kafka_producer, kafka_exception):
    with KafkaTransactionalProducer(CONFIG) as producer:
        mocked_confluent_kafka_producer.return_value.begin_transaction.side_effect = kafka_exception
        with pytest.raises(ProducerTransactionError):
            with producer.transaction():
                pass
    mocked_confluent_kafka_producer.return_value.begin_transaction.assert_called_once()
    mocked_confluent_kafka_producer.return_value.send_offsets_to_transaction.assert_not_called()
    mocked_confluent_kafka_producer.return_value.commit_transaction.assert_not_called()
    mocked_confluent_kafka_producer.return_value.abort_transaction.assert_not_called()


@pytest.mark.unit
def test_transactional_producer_raises_transaction_error_commit_tx(mocked_confluent_kafka_producer, kafka_exception):
    with KafkaTransactionalProducer(CONFIG) as producer:
        mocked_confluent_kafka_producer.return_value.commit_transaction.side_effect = kafka_exception
        with pytest.raises(ProducerTransactionError):
            with producer.transaction():
                pass
    mocked_confluent_kafka_producer.return_value.begin_transaction.assert_called_once()
    mocked_confluent_kafka_producer.return_value.send_offsets_to_transaction.assert_not_called()
    mocked_confluent_kafka_producer.return_value.commit_transaction.assert_called_once()
    mocked_confluent_kafka_producer.return_value.abort_transaction.assert_not_called()


@pytest.mark.unit
def test_producer_raises_msg_too_large_error(mocked_confluent_kafka_producer, json_topic, metric_log_event):
    with KafkaProducer(CONFIG) as producer:
        ex = KafkaException(KafkaError(error=KafkaError.MSG_SIZE_TOO_LARGE))
        mocked_confluent_kafka_producer.return_value.produce.side_effect = ex
        with pytest.raises(MessageTooLargeError):
            producer.produce(json_topic, metric_log_event)
