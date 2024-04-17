import pytest

from common.events.v1 import TestOutcomeItemSchema
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS


@pytest.mark.integration
def test_testoutcomes_endpoint(client, database_ctx, kafka_producer, headers, test_outcomes_data):
    response = client.post("/events/v1/test-outcomes", json=test_outcomes_data, headers=headers)
    assert response.status_code == 204, response.json
    assert response.data == b""
    kafka_producer.produce.assert_called_once()
    assert kafka_producer.produce.call_args.args[0] == TOPIC_UNIDENTIFIED_EVENTS
    produced_event = kafka_producer.produce.call_args.args[1]
    assert produced_event.test_outcomes == [
        TestOutcomeItemSchema().load(i) for i in test_outcomes_data["test_outcomes"]
    ]
    assert produced_event.task_key == test_outcomes_data["task_key"]


@pytest.mark.integration
def test_testoutcomes_endpoint_invalid(client, database_ctx, kafka_producer, headers, test_outcomes_data):
    # needs to be a list of objects
    test_outcomes_data["test_outcomes"] = ""
    response = client.post("/events/v1/test-outcomes", json=test_outcomes_data, headers=headers)
    assert response.status_code == 400


@pytest.mark.integration
def test_testoutcomes_endpoint_with_integration(
    client, database_ctx, kafka_producer, headers, test_outcomes_data_with_integration
):
    response = client.post("/events/v1/test-outcomes", json=test_outcomes_data_with_integration, headers=headers)
    assert response.status_code == 204


@pytest.mark.integration
def test_testoutcomes_endpoint_with_integration_invalid(
    client, database_ctx, kafka_producer, headers, test_outcomes_data_with_integration
):
    test_outcomes_data_with_integration.pop("component_integrations")
    response = client.post("/events/v1/test-outcomes", json=test_outcomes_data_with_integration, headers=headers)
    assert response.status_code == 400
