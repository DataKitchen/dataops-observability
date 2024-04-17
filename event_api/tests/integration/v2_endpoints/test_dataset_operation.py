from http import HTTPStatus
from unittest.mock import ANY

import pytest

from common.entities.event import ApiEventType
from common.events.v2 import DatasetOperationSchema, DatasetOperationType, DatasetOperationUserEvent
from common.kafka.topic import TOPIC_UNIDENTIFIED_EVENTS


@pytest.fixture
def dataset_operation_dict(dataset_dict):
    return {
        "dataset_component": dataset_dict,
        "operation": DatasetOperationType.WRITE.name,
        "path": "this/is/a/path",
    }


@pytest.mark.integration
def test_post_dataset_operation_ok(client, project, kafka_producer, headers, dataset_operation_dict):
    response = client.post("/events/v2/dataset-operation", json=dataset_operation_dict, headers=headers)
    assert response.status_code == HTTPStatus.ACCEPTED, response.json
    assert len(response.json) == 1
    assert response.json["event_id"] is not None

    event = DatasetOperationUserEvent(
        event_type=ApiEventType.DATASET_OPERATION,
        event_payload=DatasetOperationSchema().load(dataset_operation_dict),
        project_id=project.id,
        created_timestamp=ANY,
        event_id=ANY,
    )
    kafka_producer.__enter__.return_value.produce.assert_called_once_with(TOPIC_UNIDENTIFIED_EVENTS, event)


@pytest.mark.integration
def test_post_dataset_operation_invalid(client, kafka_producer, headers, dataset_operation_dict):
    dataset_operation_dict["operation"] = None
    response = client.post("/events/v2/dataset-operation", json=dataset_operation_dict, headers=headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "operation" in response.json["error"]
    kafka_producer.__enter__.return_value.produce.assert_not_called()
