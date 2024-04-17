from unittest.mock import MagicMock, patch

import pytest
from peewee import InterfaceError, OperationalError

from common.kafka.message import KafkaMessage
from rules_engine.engine import RulesEngine


@pytest.fixture
def kafka_message():
    return KafkaMessage(payload="My Payload", topic="My topic", partition=2, offset=1, headers={})


@pytest.fixture
def kafka_consumer(kafka_message):
    consumer = MagicMock()
    consumer.__iter__.return_value = iter((kafka_message,))
    return consumer


@pytest.fixture
def db_mock():
    with patch("rules_engine.engine.DB") as db:
        yield db


@pytest.fixture
def init_db_mock(db_mock):
    with patch("rules_engine.engine.init_db") as db:
        yield db


@pytest.mark.unit
def test_rules_engine_processing_failure(kafka_consumer, init_db_mock):
    init_db_mock.side_effect = [None, Exception]
    RulesEngine(event_consumer=kafka_consumer).process_events()
    # Expecting commit as we don't care about dropping kafka messages, yet.
    kafka_consumer.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.parametrize("exception", (OperationalError, InterfaceError))
def test_rules_engine_operational_db_failure(kafka_consumer, init_db_mock, exception):
    init_db_mock.side_effect = [None, exception]
    with pytest.raises(exception):
        RulesEngine(event_consumer=kafka_consumer).process_events()
    kafka_consumer.commit.assert_not_called()
