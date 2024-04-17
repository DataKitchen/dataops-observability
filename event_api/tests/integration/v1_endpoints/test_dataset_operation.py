from datetime import datetime
from http import HTTPStatus
from unittest.mock import ANY

import pytest

from common.events.enums import EventSources
from common.events.v1 import DatasetOperationEvent, DatasetOperationType, Event
from common.kafka.topic import TOPIC_UNIDENTIFIED_EVENTS


@pytest.mark.integration
def test_dataset_operation_valid(client, database_ctx, kafka_producer, headers):
    dataset_operation = {
        "dataset_key": "test key",
        "operation": DatasetOperationType.WRITE.name,
        "event_timestamp": str(datetime.now()),
        "component_tool": "asdf qwer",
    }
    response = client.post("/events/v1/dataset-operation", json=dataset_operation, headers=headers)
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert response.data == b""

    event: Event = DatasetOperationEvent.as_event_from_request(dataset_operation)
    event.received_timestamp = ANY
    event.source = EventSources.API.name
    event.event_id = ANY
    event.project_id = database_ctx.project.id
    event.event_type = DatasetOperationEvent.__name__

    kafka_producer.__enter__.return_value.produce.assert_called_once_with(TOPIC_UNIDENTIFIED_EVENTS, event)


@pytest.mark.integration
def test_status_endpoint_invalid(client, database_ctx, kafka_producer, headers):
    dataset_operation = {
        "dataset_key": "test key",
        "operation": "invalid operation",
    }
    response = client.post("/events/v1/run-status", json=dataset_operation, headers=headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.integration
def test_dataset_operation_invalid_tool(client, database_ctx, kafka_producer, headers):
    dataset_operation = {
        "dataset_key": "test key",
        "operation": DatasetOperationType.WRITE.name,
        "event_timestamp": str(datetime.now()),
        "component_tool": "invalid tool!",
    }
    response = client.post("/events/v1/dataset-operation", json=dataset_operation, headers=headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
