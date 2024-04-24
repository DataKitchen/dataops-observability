from http import HTTPStatus
from unittest.mock import ANY

import pytest

from common.entities.event import ApiEventType
from common.events.v2 import MessageLogSchema, MessageLogUserEvent
from common.kafka.topic import TOPIC_UNIDENTIFIED_EVENTS


@pytest.fixture
def log_entry_dict():
    return {"level": "INFO", "message": "Lorem ipsum"}


@pytest.fixture
def message_log_dict(component, log_entry_dict):
    return {
        "component": component,
        "log_entries": [log_entry_dict],
    }


@pytest.mark.integration
def test_post_message_log_ok(client, project, kafka_producer, headers, message_log_dict):
    response = client.post("/events/v2/message-log", json=message_log_dict, headers=headers)
    assert response.status_code == HTTPStatus.ACCEPTED, response.json
    assert len(response.json) == 1
    assert response.json["event_id"] is not None

    event = MessageLogUserEvent(
        event_type=ApiEventType.MESSAGE_LOG,
        event_payload=MessageLogSchema().load(message_log_dict),
        project_id=project.id,
        created_timestamp=ANY,
        event_id=ANY,
    )
    kafka_producer.__enter__.return_value.produce.assert_called_once_with(TOPIC_UNIDENTIFIED_EVENTS, event)


@pytest.mark.integration
def test_post_message_log_invalid(client, kafka_producer, headers, message_log_dict):
    message_log_dict["component"] = None
    response = client.post("/events/v2/message-log", json=message_log_dict, headers=headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "component" in response.json["error"]
    kafka_producer.__enter__.return_value.produce.assert_not_called()
