from datetime import datetime, timezone, UTC
from http import HTTPStatus

import pytest

from common.entities import Agent
from common.entities.agent import AgentStatus


@pytest.mark.integration
def test_agent_heartbeat(client, database_ctx, headers):
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=UTC)
    data = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "test-version",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    response = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response.status_code, response.json


@pytest.mark.integration
def test_agent_heartbeat_no_event_timestamp(client, database_ctx, headers):
    data = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "test-version",
    }
    response = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response.status_code, response.json
    agent = Agent.select().get()
    assert agent.latest_event_timestamp is None


@pytest.mark.integration
def test_agent_heartbeat_update(client, database_ctx, headers):
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=UTC)
    data = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "test-version",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    assert 0 == Agent.select().count()  # Initially there should be no registered agents
    response_1 = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_1.status_code, response_1.json

    # The latest_event_timestamp should be older than "now"
    now = datetime.now(UTC)
    agent_1 = Agent.select().get()
    assert agent_1.latest_heartbeat < now
    assert agent_1.status == AgentStatus.ONLINE

    # We hit the API again so now latest_event_timestamp should be newer than "now"
    response_2 = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_2.status_code, response_2.json
    agent_2 = Agent.select().get()
    assert agent_2.latest_heartbeat > now
    assert agent_2.status == AgentStatus.ONLINE


@pytest.mark.integration
def test_agent_heartbeat_existing_update(client, database_ctx, headers):
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=UTC)
    data_1 = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "0.1.0",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    response_1 = client.post("/agent/v1/heartbeat", json=data_1, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_1.status_code, response_1.json

    agent_1 = Agent.select().get()
    assert agent_1.latest_heartbeat is not None
    assert agent_1.latest_event_timestamp is not None
    assert agent_1.status == AgentStatus.ONLINE

    data_2 = data_1.copy()
    data_2["version"] = "12.0.3"
    data_2["latest_event_timestamp"] = datetime(2023, 10, 20, 4, 44, 44, tzinfo=UTC).isoformat()

    response_2 = client.post("/agent/v1/heartbeat", json=data_2, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_2.status_code, response_2.json
    assert 1 == Agent.select().count()  # There should still be only 1 agent
    agent_2 = Agent.select().get()
    assert "12.0.3" == agent_2.version, "Agent version should have been updated to `12.0.3`"
    assert agent_2.latest_heartbeat is not None
    assert agent_1.latest_event_timestamp is not None
    assert agent_1.version != agent_2.version, "Expected agent version to change"
