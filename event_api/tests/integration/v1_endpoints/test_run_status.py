from unittest.mock import ANY

import pytest

from common.events.enums import EventSources
from common.events.v1 import Event, RunStatusEvent
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS


@pytest.mark.integration
def test_status_endpoint(client, database_ctx, kafka_producer, headers, status_schema):
    response = client.post("/events/v1/run-status", json=status_schema, headers=headers)
    assert response.status_code == 204, response.json
    assert response.data == b""

    event: Event = RunStatusEvent.as_event_from_request(status_schema)
    event.received_timestamp = ANY
    event.source = EventSources.API.name
    event.event_id = ANY
    event.project_id = database_ctx.project.id
    event.event_type = RunStatusEvent.__name__

    kafka_producer.__enter__.return_value.produce.assert_called_once_with(TOPIC_UNIDENTIFIED_EVENTS, event)


@pytest.mark.integration
def test_status_endpoint_invalid(client, database_ctx, kafka_producer, headers, status_schema):
    # Invalid enum
    status_schema["status"] = "helloworld"
    response = client.post("/events/v1/run-status", json=status_schema, headers=headers)
    assert response.status_code == 400
