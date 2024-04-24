from copy import deepcopy
from http import HTTPStatus
from unittest.mock import ANY

import pytest

from common.entities.event import ApiEventType
from common.events.v2 import ApiRunStatus, BatchPipelineStatusSchema, BatchPipelineStatusUserEvent
from common.kafka.topic import TOPIC_UNIDENTIFIED_EVENTS


@pytest.fixture
def batch_pipeline_status_data(base_event_dict, batch_pipeline_dict):
    batch_pipeline_status = deepcopy(base_event_dict)
    batch_pipeline_status.update(
        {
            "status": ApiRunStatus.RUNNING.name,
            "batch_pipeline_component": batch_pipeline_dict,
        }
    )
    return batch_pipeline_status


@pytest.mark.integration
def test_post_run_status_ok(client, project, kafka_producer, headers, batch_pipeline_status_data):
    batch_pipeline_status_data["batch_pipeline_component"]["details"] = {"tool": "a tool"}
    batch_pipeline_status_data["batch_pipeline_component"]["run_name"] = "Wind shake establish"
    response = client.post("/events/v2/batch-pipeline-status", json=batch_pipeline_status_data, headers=headers)
    assert response.status_code == HTTPStatus.ACCEPTED, response.json
    assert len(response.json) == 1
    assert response.json["event_id"] is not None

    event = BatchPipelineStatusUserEvent(
        event_type=ApiEventType.BATCH_PIPELINE_STATUS,
        event_payload=BatchPipelineStatusSchema().load(batch_pipeline_status_data),
        project_id=project.id,
        created_timestamp=ANY,
        event_id=ANY,
    )
    kafka_producer.__enter__.return_value.produce.assert_called_once_with(TOPIC_UNIDENTIFIED_EVENTS, event)


@pytest.mark.integration
def test_post_run_status_invalid(client, test_db, kafka_producer, headers, batch_pipeline_status_data):
    batch_pipeline_status_data["status"] = "invalid status"
    response = client.post("/events/v2/batch-pipeline-status", json=batch_pipeline_status_data, headers=headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "status" in response.json["error"]
    kafka_producer.__enter__.return_value.produce.assert_not_called()


@pytest.mark.integration
def test_post_run_status_invalid_tool(client, kafka_producer, headers, batch_pipeline_status_data):
    batch_pipeline_status_data["details"] = {"tool": "invalid tool!"}
    response = client.post("/events/v2/batch-pipeline-status", json=batch_pipeline_status_data, headers=headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
