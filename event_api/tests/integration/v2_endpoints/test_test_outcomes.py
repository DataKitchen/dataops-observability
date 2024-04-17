from http import HTTPStatus
from unittest.mock import ANY

import pytest

from common.entities.event import ApiEventType
from common.events.v2 import TestOutcomesSchema, TestOutcomesUserEvent, TestStatus
from common.kafka.topic import TOPIC_UNIDENTIFIED_EVENTS


@pytest.fixture
def test_outcome_item_dict():
    return [
        {
            "name": "test name",
            "status": TestStatus.PASSED.name,
        }
    ]


@pytest.fixture
def test_outcomes_dict(component, test_outcome_item_dict):
    return {
        "component": component,
        "test_outcomes": test_outcome_item_dict,
    }


@pytest.mark.integration
def test_post_test_outcomes_ok(client, project, kafka_producer, headers, test_outcomes_dict):
    response = client.post("/events/v2/test-outcomes", json=test_outcomes_dict, headers=headers)
    assert response.status_code == HTTPStatus.ACCEPTED, response.json
    assert len(response.json) == 1
    assert response.json["event_id"] is not None

    event = TestOutcomesUserEvent(
        event_type=ApiEventType.TEST_OUTCOMES,
        event_payload=TestOutcomesSchema().load(test_outcomes_dict),
        project_id=project.id,
        created_timestamp=ANY,
        event_id=ANY,
    )
    kafka_producer.__enter__.return_value.produce.assert_called_once_with(TOPIC_UNIDENTIFIED_EVENTS, event)


@pytest.mark.integration
def test_post_test_outcomes_invalid(client, kafka_producer, headers, test_outcomes_dict):
    test_outcomes_dict["component"] = None
    response = client.post("/events/v2/test-outcomes", json=test_outcomes_dict, headers=headers)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "component" in response.json["error"]
    kafka_producer.__enter__.return_value.produce.assert_not_called()
