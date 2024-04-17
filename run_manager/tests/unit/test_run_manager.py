from unittest.mock import Mock

import pytest
from peewee import InterfaceError, OperationalError

from common.kafka import DeserializationError, ProducerTransactionError
from run_manager.run_manager import RunManager


@pytest.mark.unit
def test_run_manager_kafka_consumer_exception(kafka_producer, kafka_consumer):
    called = False

    def short_circuit_second_call():
        nonlocal called
        if not called:
            called = True
            raise DeserializationError
        else:
            assert False, "Consumer iteration called a second time instead of exiting"

    kafka_consumer.__iter__ = Mock(side_effect=short_circuit_second_call)
    rm = RunManager(kafka_consumer, kafka_producer)
    rm.process_events()  # Exception caught and return normally


@pytest.mark.unit
@pytest.mark.parametrize("exception", (OperationalError, InterfaceError))
def test_run_manager_peewee_exception(kafka_producer, kafka_consumer, patch_db, exception):
    patch_db.atomic = Mock(side_effect=exception)
    rm = RunManager(kafka_consumer, kafka_producer)
    rm.process_events()  # Exception caught and return normally
    kafka_producer.commit.assert_not_called()  # But consumtion was not commited


@pytest.mark.unit
def test_run_manager_kafka_transaction_exception(
    kafka_producer, message_log_unidentified_event, kafka_consumer, patch_db
):
    def short_circuit_second_call():
        yield (message_log_unidentified_event,)
        assert False, "Consumer iteration called a second time instead of exiting"

    kafka_consumer.__iter__.side_effect = short_circuit_second_call
    kafka_producer.transaction = Mock(side_effect=ProducerTransactionError)
    rm = RunManager(kafka_consumer, kafka_producer)
    rm.process_events()  # Exception caught and return normally
