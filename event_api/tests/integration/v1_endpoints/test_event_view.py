from http import HTTPStatus
from unittest.mock import patch

import pytest

from common.kafka import MessageTooLargeError


@pytest.mark.integration
def test_kafka_message_too_large(client, database_ctx, kafka_producer, headers, metriclog_schema):
    kafka_producer.__enter__.return_value.produce.side_effect = MessageTooLargeError()

    response = client.post("/events/v1/metric-log", json=metriclog_schema, headers=headers)

    assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE


@pytest.mark.integration
def test_request_body_too_large(flask_app, client, database_ctx, kafka_producer, headers, metriclog_schema):
    with patch.dict(flask_app.config, {"MAX_REQUEST_BODY_SIZE": 5}):
        response = client.post("/events/v1/metric-log", json=metriclog_schema, headers=headers)

    assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
