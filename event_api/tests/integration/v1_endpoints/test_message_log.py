from unittest.mock import ANY

import pytest

from common.events.enums import EventSources
from common.events.v1 import Event, MessageLogEvent
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS


@pytest.mark.integration
def test_log_endpoint(client, database_ctx, kafka_producer, headers, messagelog_schema):
    response = client.post("/events/v1/message-log", json=messagelog_schema, headers=headers)
    assert response.status_code == 204, response.json
    assert response.data == b""

    event: Event = MessageLogEvent.as_event_from_request(messagelog_schema)
    event.received_timestamp = ANY
    event.event_id = ANY
    event.source = EventSources.API.name
    event.project_id = database_ctx.project.id
    event.event_type = MessageLogEvent.__name__

    kafka_producer.__enter__.return_value.produce.assert_called_once_with(TOPIC_UNIDENTIFIED_EVENTS, event)
