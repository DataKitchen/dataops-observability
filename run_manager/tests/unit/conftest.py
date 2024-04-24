from unittest.mock import MagicMock, Mock, patch

import pytest

from common.events.v1 import MessageEventLogLevel, MessageLogEvent
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS, KafkaMessage
from testlib.fixtures.v1_events import metadata_model, pipeline_key, unidentified_event_data  # noqa: F401


@pytest.fixture
def kafka_producer():
    producer = MagicMock()
    return producer


@pytest.fixture
def message_log_unidentified_event(unidentified_event_data):
    data_copy = unidentified_event_data.copy()
    data_copy["log_level"] = MessageEventLogLevel.WARNING.name
    data_copy["message"] = "some message"
    message_log = MessageLogEvent.as_event_from_request(data_copy)
    return message_log


@pytest.fixture
def kafka_message(message_log_unidentified_event):
    return KafkaMessage(
        payload=message_log_unidentified_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def kafka_consumer(kafka_message):
    consumer = MagicMock()
    consumer.__iter__.return_value = iter((kafka_message,))
    return consumer


@pytest.fixture
def patch_db():
    with patch("run_manager.run_manager.DB", Mock()) as db:
        yield db
